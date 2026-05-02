from scholar_sink.refiner import MarkdownRefiner


class TestStripCitations:
    def test_removes_bracket_citations(self):
        text = "This is a result [12] and another [3, 5] end."
        result = MarkdownRefiner.strip_citations(text)
        assert "[12]" not in result
        assert "[3, 5]" not in result
        assert "This is a result" in result

    def test_removes_author_year_citations(self):
        text = "As shown by Jones (Jones, 2019) and Smith (Smith, 2020)."
        result = MarkdownRefiner.strip_citations(text)
        assert "(Jones, 2019)" not in result
        assert "(Smith, 2020)" not in result
        assert "As shown by Jones" in result

    def test_removes_et_al_citations(self):
        text = "Previous work (Brown et al., 2021) suggests this."
        result = MarkdownRefiner.strip_citations(text)
        assert "(Brown et al., 2021)" not in result
        assert "Previous work" in result

    def test_multiple_citation_styles_in_one_text(self):
        text = "Study [5] shows X (Smith, 2018) and (Lee et al., 2020)."
        result = MarkdownRefiner.strip_citations(text)
        assert "[5]" not in result
        assert "(Smith, 2018)" not in result
        assert "(Lee et al., 2020)" not in result
        assert "Study" in result
        assert "shows X" in result


class TestCleanHeadersFooters:
    def test_removes_arxiv_id(self):
        text = "Title\n\narXiv:2401.12345\n\nContent here."
        result = MarkdownRefiner.clean_headers_footers(text)
        assert "arXiv:2401.12345" not in result
        assert "Content here." in result

    def test_removes_preprint_notice(self):
        text = "Title\n\nPreprint submitted to Journal Name\n\nContent."
        result = MarkdownRefiner.clean_headers_footers(text)
        assert "Preprint submitted to Journal Name" not in result

    def test_removes_standalone_numbers(self):
        text = "Line 1\n123\nLine 2\n456\nLine 3"
        result = MarkdownRefiner.clean_headers_footers(text)
        assert "123" not in result
        assert "456" not in result

    def test_removes_duplicate_lines(self):
        text = "Header\n\nSame line\nSame line\nSame line\n\nFooter"
        result = MarkdownRefiner.clean_headers_footers(text)
        assert result.count("Same line") == 1


class TestIdempotency:
    def test_refine_twice_does_not_destroy_content(self):
        text = (
            "This is [12] a sample text (Smith, 2020). "
            "arXiv:2401.12345\n\n"
            "It has content that should [3] remain."
        )

        first_pass = MarkdownRefiner().refine(text)
        second_pass = MarkdownRefiner().refine(first_pass)

        assert second_pass == first_pass
        assert "sample text" in second_pass
        assert "content that should" in second_pass
        assert "remain." in second_pass

    def test_strip_citations_idempotent(self):
        text = "Result [1] and [2, 3] with (Jones, 2019)."
        first = MarkdownRefiner.strip_citations(text)
        second = MarkdownRefiner.strip_citations(first)
        assert first == second
        assert "Result" in second
        assert "with" in second


class TestExtractSections:
    def test_extracts_abstract_introduction_conclusion(self):
        text = (
            "# Abstract\n\n"
            "This is the abstract content.\n\n"
            "# Introduction\n\n"
            "This is the introduction.\n\n"
            "# Conclusion\n\n"
            "This is the conclusion."
        )
        sections = MarkdownRefiner.extract_sections(text)
        assert sections["abstract"] == "This is the abstract content."
        assert sections["introduction"] == "This is the introduction."
        assert sections["conclusion"] == "This is the conclusion."

    def test_missing_sections_return_none(self):
        text = "# Some Other Section\n\nContent here."
        sections = MarkdownRefiner.extract_sections(text)
        assert sections["abstract"] is None
        assert sections["introduction"] is None
        assert sections["conclusion"] is None
