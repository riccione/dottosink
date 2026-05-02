import re
from typing import Dict, Optional


class MarkdownRefiner:
    @staticmethod
    def strip_citations(text: str) -> str:
        patterns = [
            r"\[\d+(?:[-,]\d+)*\]",
            r"\([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*\s*,\s*\d{4}\)",
            r"\([A-Z][a-z]+\s+et\s+al\.\s*,\s*\d{4}\)",
        ]

        for pattern in patterns:
            text = re.sub(pattern, "", text)

        return text

    @staticmethod
    def clean_headers_footers(text: str) -> str:
        noise_patterns = [
            r"Preprint submitted to .+?\n",
            r"arXiv:\d+\.\d+",
            r"^\s*\d+\s*$",
            r"^\s*www\..+?\s*$",
        ]

        for pattern in noise_patterns:
            text = re.sub(pattern, "", text, flags=re.MULTILINE)

        lines = text.splitlines()
        cleaned = []
        prev = None
        for line in lines:
            stripped = line.strip()
            if stripped and stripped != prev:
                cleaned.append(line)
            prev = stripped

        return "\n".join(cleaned)

    @staticmethod
    def extract_sections(text: str) -> Dict[str, Optional[str]]:
        sections = {"abstract": None, "introduction": None, "conclusion": None}

        patterns = {
            "abstract": r"^#+\s*abstract\s*$",
            "introduction": r"^#+\s*introduction\s*$",
            "conclusion": r"^#+\s*conclusion.*$",
        }

        positions = []
        for key, pattern in patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                positions.append((match.start(), key))

        positions.sort()

        for i, (pos, key) in enumerate(positions):
            start = pos
            end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
            section_text = text[start:end].strip()
            lines = section_text.splitlines()
            if len(lines) > 1:
                section_text = "\n".join(lines[1:]).strip()
            sections[key] = section_text

        return sections

    def refine(self, text: str) -> str:
        text = self.strip_citations(text)
        text = self.clean_headers_footers(text)
        return text
