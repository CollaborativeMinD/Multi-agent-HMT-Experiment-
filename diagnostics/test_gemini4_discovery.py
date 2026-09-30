"""Offline tests for Gemini 4 Argon metadata discovery."""
from __future__ import annotations
import ast
import unittest
from pathlib import Path
import gemini4_discovery as g

class Gemini4DiscoveryTests(unittest.TestCase):
    def test_selects_name_display_or_description_matches(self) -> None:
        rows = [
            {"name": "models/gemini-4-argon", "displayName": "Gemini 4 Argon"},
            {"name": "models/other", "displayName": "Other", "description": "Argon preview"},
            {"name": "models/gemini-3.8-flash", "displayName": "Gemini 3.8 Flash"},
        ]
        self.assertEqual(len(g.select_matches(rows)), 2)

    def test_model_view_excludes_description_and_unknown_fields(self) -> None:
        row = {"name": "models/gemini-4-argon", "displayName": "Gemini 4 Argon",
               "description": "not persisted", "inputTokenLimit": 10, "outputTokenLimit": 20,
               "supportedGenerationMethods": ["generateContent"], "secretish": "drop"}
        view = g.model_view(row)
        self.assertNotIn("description", view)
        self.assertNotIn("secretish", view)
        self.assertEqual(view["outputTokenLimit"], 20)

    def test_functions_fit_line_limit(self) -> None:
        path = Path(g.__file__)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        long = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                size = int(node.end_lineno or node.lineno) - node.lineno + 1
                if size > 60:
                    long[node.name] = size
        self.assertEqual(long, {})

if __name__ == "__main__":
    unittest.main()
