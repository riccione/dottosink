import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def convert_pdf_to_md(pdf_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{pdf_path.stem}.md"

    try:
        _convert_with_marker(pdf_path, md_path)
    except Exception as e:
        logger.warning(f"Marker conversion failed: {e}. Falling back to PyMuPDF.")
        _convert_with_pymupdf(pdf_path, md_path)

    return md_path


def _convert_with_marker(pdf_path: Path, md_path: Path) -> None:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered

    artifact_dict = create_model_dict()
    converter = PdfConverter(artifact_dict=artifact_dict)
    rendered = converter(str(pdf_path))
    text, _, _ = text_from_rendered(rendered)

    md_path.write_text(text, encoding="utf-8")


def _convert_with_pymupdf(pdf_path: Path, md_path: Path) -> None:
    import fitz

    doc = fitz.open(pdf_path)
    text = "\n\n".join(page.get_text() for page in doc)
    doc.close()

    md_path.write_text(text, encoding="utf-8")
