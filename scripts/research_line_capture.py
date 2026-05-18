#!/usr/bin/env python3
"""NOUS OS Research Line — L1 daily capture.

Fetches a small set of high-signal RSS sources, filters entries by anchor
keywords, and writes one markdown file per day at:

    docs/research-line/inbound/_inbox/YYYY-MM-DD.md

This is the L1 layer of the three-tier external-input loop defined in
docs/research-line/research-line.md. It is intentionally narrow (≤8
sources, ≤2 weeks of history per source) and intentionally dumb (no LLM
judgment — pure pattern match). L2 triage promotes 1-3 of these per week
to full inbound notes; the cron does not auto-promote.

Designed to run in GitHub Actions. No third-party dependencies — only
Python stdlib so the workflow runs on a clean ubuntu-latest with the
default Python setup.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
INBOX_DIR = ROOT / "docs" / "research-line" / "inbound" / "_inbox"
USER_AGENT = "nous-os-research-line-capture/0.1 (+https://nousos.ai)"
REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_HISTORY_DAYS = 2


# Sources for L1 capture. Each must expose RSS or Atom. Keep this list small
# and reliable — 5-8 sources is the design point. When adding, prefer feeds
# that publish at most a handful of items per day.
SOURCES: list[dict] = [
    {
        "id": "arxiv-cs-hc",
        "title": "arXiv cs.HC",
        "url": "http://export.arxiv.org/rss/cs.HC",
        "bucket": "3 · AI literacy / HCI",
    },
    {
        "id": "arxiv-cs-cy",
        "title": "arXiv cs.CY",
        "url": "http://export.arxiv.org/rss/cs.CY",
        "bucket": "3 · AI literacy / HCI",
    },
    {
        "id": "mollick-one-useful-thing",
        "title": "Ethan Mollick · One Useful Thing",
        "url": "https://www.oneusefulthing.org/feed",
        "bucket": "6 · Individual essays & podcasts",
    },
    {
        "id": "matuschak-blog",
        "title": "Andy Matuschak",
        "url": "https://andymatuschak.org/feed.xml",
        "bucket": "6 · Individual essays & podcasts",
    },
    {
        "id": "openai-news",
        "title": "OpenAI · News",
        "url": "https://openai.com/news/rss.xml",
        "bucket": "4 · Industry research",
    },
]


# Anchor keywords. An entry is kept if its title or summary contains any of
# these (case-insensitive). Order does not matter; first-match wins for the
# annotation. Keep this list short — broad keywords like "AI" alone produce
# firehose noise and must not appear here.
KEYWORDS: list[str] = [
    "AI literacy",
    "AI tutor",
    "AI scaffolding",
    "AI in education",
    "AI in the classroom",
    "cognitive offloading",
    "tools for thought",
    "self-regulated learning",
    "metacognition",
    "human-AI",
    "co-evolution",
    "human agency",
    "boundary",
    "ZPD",
    "scaffolding",
    "capability delta",
    "calibrated trust",
    "transformative tool",
    "constitutional AI",
    "alignment",
    "interpretability",
]


# ---------------------------------------------------------------------------
# Data shape
# ---------------------------------------------------------------------------


@dataclass
class CapturedEntry:
    source_id: str
    source_title: str
    bucket: str
    title: str
    link: str
    published: str  # ISO-ish; may be empty if not available
    summary: str
    matched_keywords: list[str]


# ---------------------------------------------------------------------------
# Fetching and parsing
# ---------------------------------------------------------------------------


def _http_get(url: str, *, timeout: int = REQUEST_TIMEOUT_SECONDS) -> bytes:
    """Fetch a URL and return raw bytes. Caller handles exceptions."""

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def _strip_html(text: str) -> str:
    """Crude HTML→text. Enough for RSS summaries; not a full parser."""

    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _truncate(text: str, limit: int = 240) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"


def parse_feed(xml_bytes: bytes) -> list[dict]:
    """Parse an RSS 2.0 or Atom feed into a list of normalized entry dicts.

    Returns entries with keys: title, link, published, summary.
    Skips entries that fail to parse rather than raising.
    """

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    entries: list[dict] = []
    # RSS 2.0
    for item in root.iter("item"):
        entries.append(
            {
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "published": (
                    item.findtext("pubDate")
                    or item.findtext("{http://purl.org/dc/elements/1.1/}date")
                    or ""
                ).strip(),
                "summary": _strip_html(
                    item.findtext("description")
                    or item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded")
                    or ""
                ),
            }
        )
    # Atom
    atom_ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(f"{atom_ns}entry"):
        link_el = entry.find(f"{atom_ns}link")
        link = (link_el.get("href") if link_el is not None else "") or ""
        entries.append(
            {
                "title": (entry.findtext(f"{atom_ns}title") or "").strip(),
                "link": link.strip(),
                "published": (
                    entry.findtext(f"{atom_ns}published")
                    or entry.findtext(f"{atom_ns}updated")
                    or ""
                ).strip(),
                "summary": _strip_html(
                    entry.findtext(f"{atom_ns}summary")
                    or entry.findtext(f"{atom_ns}content")
                    or ""
                ),
            }
        )

    return entries


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------


def match_keywords(haystack: str, keywords: Iterable[str]) -> list[str]:
    """Return the keywords found in `haystack` (case-insensitive substring)."""

    lowered = haystack.lower()
    return [kw for kw in keywords if kw.lower() in lowered]


def _parse_pub_date(raw: str) -> datetime | None:
    """Best-effort parse of RFC 822, ISO 8601, and a few common variants."""

    if not raw:
        return None
    raw = raw.strip()
    # ISO 8601 (Atom)
    for trial in (raw, raw.replace("Z", "+00:00")):
        try:
            return datetime.fromisoformat(trial)
        except ValueError:
            pass
    # RFC 822 (RSS pubDate)
    rfc_formats = (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S GMT",
        "%a, %d %b %Y %H:%M:%S",
    )
    for fmt in rfc_formats:
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def is_recent(entry: dict, *, max_age_days: int) -> bool:
    """Keep entries with no parseable date (assume recent) or within window."""

    dt = _parse_pub_date(entry.get("published", ""))
    if dt is None:
        return True
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    return dt >= cutoff


def filter_entries(
    entries: list[dict],
    *,
    source: dict,
    keywords: Iterable[str],
    max_age_days: int,
) -> list[CapturedEntry]:
    """Apply keyword + recency filters; produce CapturedEntry list."""

    keep: list[CapturedEntry] = []
    for entry in entries:
        if not entry.get("title") or not entry.get("link"):
            continue
        if not is_recent(entry, max_age_days=max_age_days):
            continue
        haystack = f"{entry['title']} {entry.get('summary', '')}"
        hits = match_keywords(haystack, keywords)
        if not hits:
            continue
        keep.append(
            CapturedEntry(
                source_id=source["id"],
                source_title=source["title"],
                bucket=source["bucket"],
                title=entry["title"],
                link=entry["link"],
                published=entry.get("published", ""),
                summary=_truncate(entry.get("summary", "")),
                matched_keywords=hits,
            )
        )
    return keep


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def render_markdown(
    *,
    capture_date: str,
    by_source: dict[str, tuple[dict, list[CapturedEntry], str | None]],
) -> str:
    """Render the daily inbox markdown.

    `by_source` maps source_id → (source_meta, entries_kept, error_or_None).
    """

    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: \"L1 capture · {capture_date}\"")
    lines.append(f"captured: {capture_date}")
    lines.append("layer: L1")
    lines.append("status: raw  # awaiting L2 triage")
    lines.append("---")
    lines.append("")
    lines.append(f"# L1 capture · {capture_date}")
    lines.append("")
    lines.append(
        "Raw daily snapshot from the NOUS OS Research Line capture cron. Entries "
        "are filtered by anchor keywords only; no LLM judgment has been applied. "
        "L2 triage promotes 1–3 of these to full inbound notes per week."
    )
    lines.append("")

    total_kept = sum(len(entries) for _, entries, _ in by_source.values())
    sources_ok = sum(1 for _, _, err in by_source.values() if err is None)
    sources_total = len(by_source)
    lines.append(
        f"**Summary:** {total_kept} entries kept · "
        f"{sources_ok}/{sources_total} sources fetched OK"
    )
    lines.append("")

    for source_id, (source, entries, error) in by_source.items():
        lines.append(f"## {source['title']}")
        lines.append("")
        lines.append(f"- **Source:** `{source_id}` · bucket {source['bucket']}")
        lines.append(f"- **URL:** {source['url']}")
        if error is not None:
            lines.append(f"- **Fetch:** ❌ {error}")
            lines.append("")
            continue
        lines.append(f"- **Fetch:** ✅ kept {len(entries)} match{'es' if len(entries) != 1 else ''}")
        lines.append("")
        if not entries:
            lines.append("> No matches in this source today.")
            lines.append("")
            continue
        for entry in entries:
            kw_str = ", ".join(f"`{kw}`" for kw in entry.matched_keywords)
            lines.append(f"### {entry.title}")
            lines.append("")
            lines.append(f"- {entry.link}")
            if entry.published:
                lines.append(f"- Published: {entry.published}")
            lines.append(f"- Matched: {kw_str}")
            if entry.summary:
                lines.append("")
                lines.append(f"> {entry.summary}")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "*L2 action:* promote any entry to a full 1-page note in "
        "`docs/research-line/inbound/` using the inbound `_template.md`, then "
        "flip the corresponding `anchor-atlas.md` entry from `queued`/`scanned` "
        "to `note-written`."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def capture(
    *,
    sources: list[dict] = SOURCES,
    keywords: list[str] = KEYWORDS,
    max_age_days: int = DEFAULT_HISTORY_DAYS,
    capture_date: str | None = None,
    fetcher=_http_get,
) -> tuple[str, str]:
    """Run one capture cycle. Returns (capture_date, markdown_text)."""

    capture_date = capture_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    by_source: dict[str, tuple[dict, list[CapturedEntry], str | None]] = {}
    for source in sources:
        try:
            raw = fetcher(source["url"])
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            by_source[source["id"]] = (source, [], f"{type(exc).__name__}: {exc}")
            continue
        entries = parse_feed(raw)
        kept = filter_entries(
            entries,
            source=source,
            keywords=keywords,
            max_age_days=max_age_days,
        )
        by_source[source["id"]] = (source, kept, None)
    return capture_date, render_markdown(capture_date=capture_date, by_source=by_source)


def write_inbox_file(capture_date: str, markdown: str, *, inbox_dir: Path = INBOX_DIR) -> Path:
    inbox_dir.mkdir(parents=True, exist_ok=True)
    out_path = inbox_dir / f"{capture_date}.md"
    out_path.write_text(markdown, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="NOUS OS Research Line L1 daily capture.")
    parser.add_argument(
        "--capture-date",
        default=None,
        help="Override the YYYY-MM-DD label on the output file (default: today UTC).",
    )
    parser.add_argument(
        "--max-age-days",
        type=int,
        default=DEFAULT_HISTORY_DAYS,
        help="Skip entries older than this many days (default: 2).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print to stdout instead of writing to docs/research-line/inbound/_inbox/.",
    )
    args = parser.parse_args()

    capture_date, markdown = capture(
        max_age_days=args.max_age_days,
        capture_date=args.capture_date,
    )

    if args.dry_run:
        print(markdown)
        return 0

    out_path = write_inbox_file(capture_date, markdown)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
