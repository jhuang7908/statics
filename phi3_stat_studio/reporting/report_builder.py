"""Generate HTML/PDF reports from analysis outputs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import CONFIG

try:
    from weasyprint import HTML  # type: ignore
except Exception:  # pragma: no cover
    HTML = None  # type: ignore


MISSING_WEASYPRINT_MESSAGE = (
    "PDF export requires WeasyPrint native dependencies. "
    "Please follow https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation "
    "or export HTML instead."
)


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(CONFIG.paths.templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )


@dataclass
class ReportBuilder:
    language: str = CONFIG.default_language

    def _template(self):
        return _env().get_template("report.html")

    def render_html(self, context: Dict[str, Any]) -> str:
        template = self._template()
        return template.render(**context)

    def save_html(self, context: Dict[str, Any], output_path: Path) -> Path:
        html = self.render_html(context)
        output_path.write_text(html, encoding="utf-8")
        return output_path

    def save_pdf(self, context: Dict[str, Any], output_path: Path) -> Path:
        if HTML is None:
            raise RuntimeError(MISSING_WEASYPRINT_MESSAGE)
        html = self.render_html(context)
        HTML(string=html).write_pdf(str(output_path))
        return output_path
