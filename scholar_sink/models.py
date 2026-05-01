from pydantic import BaseModel
from typing import Optional, List


class Paper(BaseModel):
    arxiv_id: str
    title: str
    authors: List[str]
    published: str
    summary: str
    pdf_path: Optional[str] = None
    md_path: Optional[str] = None
    pdf_url: Optional[str] = None
    status: str = "pending"  # pending, downloaded, processed, failed
