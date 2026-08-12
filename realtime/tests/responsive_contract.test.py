from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.references = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        self.tags.append((tag, values))
        if "id" in values: self.ids.add(values["id"])
        for name in ("href", "src", "aria-describedby", "aria-controls"):
            if name in values: self.references.append((name, values[name]))


class ResponsiveAccessibilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "client/index.html").read_text()
        cls.css = (ROOT / "client/styles.css").read_text()
        cls.script = (ROOT / "client/app.js").read_text()
        cls.parser = PageParser(); cls.parser.feed(cls.html)

    def test_responsive_breakpoints_stack_at_1100_and_cover_narrow_and_projector(self):
        self.assertRegex(self.css, r"@media \(max-width: 1100px\)")
        self.assertRegex(self.css, r"@media \(max-width: 767px\)")
        self.assertRegex(self.css, r"@media \(max-width: 420px\)")
        self.assertRegex(self.css, r"@media \(min-width: 2200px\)")
        stack = self.css.split("@media (max-width: 1100px)", 1)[1].split("@media (max-width: 767px)", 1)[0]
        self.assertIn(".source-grid, .decision-grid, .evidence-grid", stack)
        self.assertIn("grid-template-columns: 1fr", stack)
        self.assertNotRegex(self.css, r"body\s*\{[^}]*min-width")
        self.assertNotRegex(self.css, r"overflow-x:\s*(?:hidden|clip)")
        self.assertIn("width: min(100%, 1640px)", self.css)
        self.assertIn("width: min(100%, 1880px)", self.css)
        self.assertIn("font-size: 28px", self.css)

    def test_accessibility_landmarks_labels_charts_fallback_and_keyboard_hooks(self):
        self.assertEqual(len([1 for tag, _ in self.parser.tags if tag == "h1"]), 1)
        self.assertTrue(any(tag == "main" for tag, _ in self.parser.tags))
        self.assertTrue(any(tag == "nav" and values.get("aria-label") for tag, values in self.parser.tags))
        self.assertTrue(any(tag == "fieldset" and values.get("id") == "sample-list" for tag, values in self.parser.tags))
        self.assertTrue(any(tag == "legend" for tag, _ in self.parser.tags))
        canvases = [values for tag, values in self.parser.tags if tag == "canvas"]
        self.assertEqual(len(canvases), 5)
        self.assertTrue(all(value.get("role") == "img" and value.get("aria-describedby") in self.parser.ids for value in canvases))
        self.assertGreaterEqual(len([1 for tag, _ in self.parser.tags if tag == "caption"]), 2)
        self.assertIn(":focus-visible", self.css)
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn('event.key === "Escape"', self.script)
        self.assertIn('event.key === " "', self.script)
        self.assertIn("canvas.tabIndex = 0", self.script)
        self.assertIn("ArrowLeft", self.script)
        self.assertIn("aria-live=\"polite\"", self.html)
        self.assertIn("role=\"alert\"", self.html)

    def test_local_references_and_controls_are_bounded(self):
        for name, reference in self.parser.references:
            if reference.startswith("#"):
                self.assertIn(reference[1:], self.parser.ids)
            if name in {"href", "src"}:
                self.assertNotRegex(reference, r"^(?:https?:)?//")
        for tag, values in self.parser.tags:
            if tag == "a":
                self.assertNotEqual(values.get("download"), "")
                self.assertNotIn("target", values)
            if tag == "input":
                self.assertNotEqual(values.get("type"), "file")
        combined = self.html + self.script
        for token in ("<audio", "<video", "<iframe", "download=", "form action=", "onclick=", "onload="):
            self.assertNotIn(token, combined.lower())

    def test_service_and_deployment_templates_fail_closed_without_route_mutation(self):
        service = (ROOT / "deploy/firstmate-silent-speech-demo.service").read_text()
        preflight = (ROOT / "deploy/preflight.sh").read_text()
        deploy = (ROOT / "deploy/deploy.sh").read_text()
        rollback = (ROOT / "deploy/rollback.sh").read_text()
        verify = (ROOT / "deploy/verify.sh").read_text()
        self.assertIn("User=quiet-channel-replay", service)
        self.assertIn("Group=quiet-channel-replay", service)
        self.assertIn("--host 127.0.0.1 --port 8765 --no-access-log", service)
        for hardening in ("NoNewPrivileges=true", "PrivateTmp=true", "ProtectSystem=strict", "ProtectHome=true", "IPAddressDeny=any", "IPAddressAllow=localhost"):
            self.assertIn(hardening, service)
        self.assertIn("QUIET_CHANNEL_REQUIRE_RELEASE_BINDING=1", service)
        self.assertNotIn("0.0.0.0", service)
        self.assertIn("https://srv1834218.tail8a7378.ts.net:8449", preflight)
        self.assertIn("http://127.0.0.1:8765", preflight)
        self.assertNotRegex(preflight, r"systemctl\s+(?:start|stop|restart|enable|disable)")
        scripts = "\n".join((preflight, deploy, rollback, verify))
        self.assertNotRegex(scripts, r"tailscale\s+serve\s+(?:--|https|tcp|set)")
        self.assertNotRegex(scripts, r"tailscale\s+funnel\s+(?:--|on|off|set)")
        self.assertIn("s/fd=[0-9]+/fd=*/g", deploy)
        self.assertIn("s/fd=[0-9]+/fd=*/g", verify)
        self.assertIn("loopback readiness did not become available", verify)
        self.assertIn("wildcard backend bind detected", verify)
        self.assertIn("QUIET_CHANNEL_DEPLOY_AUTHORIZED", deploy)
        self.assertIn("QUIET_CHANNEL_DEPLOY_AUTHORIZED", rollback)
        self.assertIn("QUIET_CHANNEL_LEGACY_ROLLBACK_STATE", deploy)
        self.assertIn("application_revision", deploy)
        self.assertIn("QUIET_CHANNEL_RELEASE_REVISION", deploy)
        self.assertIn("QUIET_CHANNEL_RELEASE_REVISION", rollback)
        self.assertNotRegex(deploy, r"generate_release_manifest\.py[^\n]*--revision")
        self.assertIn("mv -Tf", deploy)
        self.assertIn("mv -Tf", rollback)
        self.assertIn("firstmate-silent-speech-demo.service", scripts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
