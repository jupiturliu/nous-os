from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResearchPageTests(unittest.TestCase):
    def test_research_track_uses_friendly_page_not_raw_markdown_as_primary_path(self) -> None:
        homepage = (ROOT / "index.html").read_text()
        research = (ROOT / "research.html").read_text()
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()

        self.assertIn('<a href="/research.html">Research</a>', homepage)
        self.assertIn('href="/research.html#anchor"', homepage)
        self.assertIn('href="/research.html#model"', homepage)
        self.assertIn('href="/research.html#metrics"', homepage)
        self.assertNotIn('href="/docs/human-ai-symbiosis-self-evolution.md"', homepage)
        self.assertNotIn('href="/docs/human-ai-coevolution-model-v0.md"', homepage)
        self.assertNotIn('href="/docs/self-evolution-metrics-v0.md"', homepage)

        self.assertIn("How can humans and AI learn to think better together?", research)
        self.assertIn("The website page is the user-friendly reading layer.", research)
        self.assertIn("Theory anchor MD", research)
        self.assertIn("Launch Student Sandbox", research)
        self.assertIn('<link rel="icon" href="favicon.svg" type="image/svg+xml">', research)
        self.assertIn("cp research.html _site/", workflow)


if __name__ == "__main__":
    unittest.main()
