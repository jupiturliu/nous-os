"""Contract tests for the Research Line L1 daily capture script.

These tests intentionally do NOT make any network calls. They use mocked
fetchers so the test suite is deterministic and works offline.

What they protect against:
- RSS / Atom parser regressions
- Keyword filter logic regressions
- Markdown output shape changes (downstream tools read this)
- Inadvertent removal of required sections in the output template
"""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import research_line_capture as cap  # noqa: E402


RSS_FIXTURE = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Fixture Feed</title>
    <item>
      <title>A paper on AI literacy and scaffolding</title>
      <link>https://example.org/paper-1</link>
      <pubDate>__RECENT__</pubDate>
      <description>This paper studies AI literacy in classrooms and proposes scaffolding patterns.</description>
    </item>
    <item>
      <title>A paper on completely unrelated topology</title>
      <link>https://example.org/paper-2</link>
      <pubDate>__RECENT__</pubDate>
      <description>Algebraic topology results unrelated to anything in our research line.</description>
    </item>
    <item>
      <title>An old paper on AI literacy</title>
      <link>https://example.org/paper-old</link>
      <pubDate>Mon, 01 Jan 2020 00:00:00 +0000</pubDate>
      <description>AI literacy in 2020.</description>
    </item>
  </channel>
</rss>
"""


ATOM_FIXTURE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Fixture Atom</title>
  <entry>
    <title>An essay on tools for thought and cognitive offloading</title>
    <link href="https://example.org/atom-1"/>
    <updated>__RECENT_ISO__</updated>
    <summary>Tools for thought essay arguing against cognitive offloading.</summary>
  </entry>
  <entry>
    <title>Unrelated essay</title>
    <link href="https://example.org/atom-2"/>
    <updated>__RECENT_ISO__</updated>
    <summary>Talks about gardening.</summary>
  </entry>
</feed>
"""


def _now_recent_rfc822() -> str:
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")


def _now_recent_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _hydrate_rss() -> bytes:
    return RSS_FIXTURE.replace(b"__RECENT__", _now_recent_rfc822().encode("utf-8"))


def _hydrate_atom() -> bytes:
    return ATOM_FIXTURE.replace(b"__RECENT_ISO__", _now_recent_iso().encode("utf-8"))


class ParseFeedTests(unittest.TestCase):
    def test_parses_rss_2_items(self) -> None:
        entries = cap.parse_feed(_hydrate_rss())
        self.assertEqual(len(entries), 3)
        titles = {e["title"] for e in entries}
        self.assertIn("A paper on AI literacy and scaffolding", titles)

    def test_parses_atom_items(self) -> None:
        entries = cap.parse_feed(_hydrate_atom())
        self.assertEqual(len(entries), 2)
        links = {e["link"] for e in entries}
        self.assertIn("https://example.org/atom-1", links)

    def test_malformed_xml_returns_empty_list(self) -> None:
        self.assertEqual(cap.parse_feed(b"not xml at all"), [])


class KeywordFilterTests(unittest.TestCase):
    def test_match_keywords_is_case_insensitive(self) -> None:
        hits = cap.match_keywords("Studying COGNITIVE OFFLOADING in classrooms.", cap.KEYWORDS)
        self.assertIn("cognitive offloading", hits)

    def test_filter_keeps_only_matching_recent_entries(self) -> None:
        rss = _hydrate_rss()
        entries = cap.parse_feed(rss)
        source = {"id": "test", "title": "Test", "url": "x", "bucket": "9 · test"}
        kept = cap.filter_entries(
            entries, source=source, keywords=cap.KEYWORDS, max_age_days=2
        )
        self.assertEqual(len(kept), 1, f"expected 1 kept, got {[k.title for k in kept]}")
        self.assertEqual(kept[0].link, "https://example.org/paper-1")
        self.assertIn("AI literacy", kept[0].matched_keywords)

    def test_old_entries_are_filtered_out(self) -> None:
        # The fixture has one explicitly-2020 entry; it must be rejected at
        # max_age_days=2 even if its title matches a keyword.
        rss = _hydrate_rss()
        entries = cap.parse_feed(rss)
        source = {"id": "test", "title": "Test", "url": "x", "bucket": "9 · test"}
        kept = cap.filter_entries(
            entries, source=source, keywords=cap.KEYWORDS, max_age_days=2
        )
        self.assertNotIn("https://example.org/paper-old", [k.link for k in kept])

    def test_filter_drops_entries_without_link(self) -> None:
        bad = [{"title": "matches scaffolding", "link": "", "summary": "", "published": ""}]
        source = {"id": "test", "title": "Test", "url": "x", "bucket": "9 · test"}
        kept = cap.filter_entries(
            bad, source=source, keywords=cap.KEYWORDS, max_age_days=2
        )
        self.assertEqual(kept, [])


class CaptureOrchestrationTests(unittest.TestCase):
    def test_capture_writes_well_formed_markdown(self) -> None:
        sources = [
            {"id": "src-a", "title": "Source A", "url": "https://a/feed", "bucket": "9 · test"},
            {"id": "src-b", "title": "Source B", "url": "https://b/feed", "bucket": "9 · test"},
        ]
        responses = {
            "https://a/feed": _hydrate_rss(),
            "https://b/feed": _hydrate_atom(),
        }

        def fake_fetcher(url, **_):
            return responses[url]

        capture_date, markdown = cap.capture(
            sources=sources,
            keywords=cap.KEYWORDS,
            max_age_days=2,
            capture_date="2026-05-17",
            fetcher=fake_fetcher,
        )

        self.assertEqual(capture_date, "2026-05-17")
        # Front-matter
        self.assertTrue(markdown.startswith("---\n"), "expected YAML front-matter")
        self.assertIn("layer: L1", markdown)
        self.assertIn("status: raw", markdown)
        # Summary line
        self.assertIn("2/2 sources fetched OK", markdown)
        # Both sources are represented even if one has zero matches
        self.assertIn("## Source A", markdown)
        self.assertIn("## Source B", markdown)
        # The keyword-matched entries appear; the unrelated ones do not
        self.assertIn("https://example.org/paper-1", markdown)
        self.assertIn("https://example.org/atom-1", markdown)
        self.assertNotIn("https://example.org/paper-2", markdown)
        self.assertNotIn("https://example.org/atom-2", markdown)
        # L2 action footer
        self.assertIn("L2 action", markdown)
        self.assertIn("anchor-atlas.md", markdown)

    def test_capture_records_fetch_error_per_source(self) -> None:
        sources = [
            {"id": "broken", "title": "Broken", "url": "https://broken", "bucket": "9 · test"},
        ]

        def fail_fetcher(url, **_):
            raise OSError("connection refused")

        capture_date, markdown = cap.capture(
            sources=sources,
            keywords=cap.KEYWORDS,
            max_age_days=2,
            capture_date="2026-05-17",
            fetcher=fail_fetcher,
        )

        self.assertIn("0/1 sources fetched OK", markdown)
        self.assertIn("❌ OSError: connection refused", markdown)

    def test_default_source_list_is_small_and_diverse(self) -> None:
        """Wave 3 design point: keep L1 narrow. Sanity-check we have not
        ballooned the source list. Five buckets covered, ≤ 8 sources, every
        source has a bucket label aligned with the anchor atlas."""

        self.assertLessEqual(len(cap.SOURCES), 8, "L1 must stay narrow")
        self.assertGreaterEqual(len(cap.SOURCES), 3, "need at least 3 sources for diversity")
        bucket_prefixes = {s["bucket"][0] for s in cap.SOURCES}
        self.assertGreaterEqual(len(bucket_prefixes), 2, "need ≥ 2 buckets represented")
        for source in cap.SOURCES:
            for required_key in ("id", "title", "url", "bucket"):
                self.assertIn(required_key, source, f"source missing {required_key!r}")


class CronWorkflowExistsTests(unittest.TestCase):
    """The capture script is only useful if the workflow that runs it on a
    schedule exists. Guard against the workflow drifting out of sync."""

    def test_capture_workflow_file_exists_and_is_scheduled(self) -> None:
        workflow_path = ROOT / ".github" / "workflows" / "research-line-capture.yml"
        self.assertTrue(workflow_path.exists(), "research-line-capture.yml must exist")
        workflow = workflow_path.read_text(encoding="utf-8")

        # Must be on a daily-ish cron schedule.
        self.assertIn("schedule:", workflow)
        self.assertIn("cron:", workflow)
        # Must run the capture script.
        self.assertIn("scripts/research_line_capture.py", workflow)
        # Must open a PR (no direct master commits — operator-gated triage).
        self.assertIn("gh pr create", workflow)
        # Must NOT auto-merge.
        self.assertNotIn("gh pr merge", workflow)


if __name__ == "__main__":
    unittest.main()
