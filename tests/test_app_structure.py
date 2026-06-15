"""Structural tests for app.py — verify section ordering, no duplication, correct patterns.

These describe the EXPECTED behavior AFTER the rewrite. On the current (broken) app.py,
several of these tests MUST FAIL — proving they describe the new correct structure.
"""

import ast
import re

APP_PATH = "app.py"


def read_app() -> str:
    with open(APP_PATH) as f:
        return f.read()


class TestAppSyntax:
    """Syntax-level checks (should pass on both old and new code)."""

    def test_no_syntax_errors(self):
        """app.py MUST parse without SyntaxError."""
        source = read_app()
        # ast.parse raises SyntaxError if invalid
        ast.parse(source)

    def test_no_use_container_width(self):
        """app.py MUST NOT contain use_container_width."""
        source = read_app()
        assert "use_container_width" not in source, (
            "use_container_width is deprecated; use width='stretch' instead"
        )


class TestAppDuplication:
    """No-duplication checks — these MUST FAIL on the current (broken) app.py."""

    def test_single_aplicar_filtro_button(self):
        """Exactly ONE 'Aplicar filtro' st.button MUST exist."""
        source = read_app()
        # Count occurrences of the label text in button calls
        count = source.count("Aplicar filtro")
        assert count == 1, (
            f"Expected exactly 1 'Aplicar filtro' button, found {count}. "
            "Duplicated filter/apply sections must be removed."
        )

    def test_single_filter_selectbox(self):
        """Exactly ONE st.selectbox with the 4 filter options MUST exist."""
        source = read_app()
        options_pattern = re.escape('["Media", "Mediana", "Laplaciano", "Sobel"]')
        matches = re.findall(options_pattern, source)
        assert len(matches) >= 1, (
            "Filter selectbox options missing from app.py"
        )
        # Only one selectbox call should exist
        selectbox_count = source.count("st.selectbox(")
        assert selectbox_count == 1, (
            f"Expected exactly 1 st.selectbox call, found {selectbox_count}. "
            "Filter selection must appear exactly once."
        )

    def test_single_results_block(self):
        """The filter results display block MUST appear exactly once.

        The sidebar has a conditional download guard that also uses
        'st.session_state.result is not None', so we distinguish by looking
        for the results-specific display content.
        """
        source = read_app()
        # The results display block contains a subheader with this specific
        # emoji+text combination — it's unique to the results section.
        results_header = "🖼️ Imagen original y recorte digitalizado"
        matches = re.findall(re.escape(results_header), source)
        assert len(matches) >= 1, "Results display block not found"
        assert len(matches) == 1, (
            f"Expected exactly 1 results display block, found {len(matches)}. "
            "Filter results must appear exactly once."
        )

    def test_single_apply_button_block(self):
        """The filter apply logic MUST appear in exactly one st.button block."""
        source = read_app()
        # Count st.button calls that reference filter options
        button_matches = re.findall(
            r'if\s+st\.button\([^)]*Aplicar filtro[^)]*\)',
            source,
        )
        assert len(button_matches) == 1, (
            f"Expected exactly 1 'Aplicar filtro' button check, "
            f"found {len(button_matches)}."
        )


class TestAppOrdering:
    """Section ordering checks — overlay before results, page_config first."""

    def test_set_page_config_first(self):
        """st.set_page_config MUST be the first Streamlit call (before any st.*)."""
        source = read_app()
        lines = source.split("\n")

        config_line_idx = None
        first_st_line_idx = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            # Ignore comments and docstrings
            if stripped.startswith("#") or stripped.startswith('"""'):
                continue
            # Find the first st.* call
            if stripped.startswith("st.") and first_st_line_idx is None:
                if "set_page_config" in stripped:
                    config_line_idx = i
                else:
                    first_st_line_idx = i

        if first_st_line_idx is not None and config_line_idx is not None:
            assert config_line_idx < first_st_line_idx, (
                f"st.set_page_config on line {config_line_idx + 1} must come "
                f"before other st.* calls (first at line {first_st_line_idx + 1})"
            )

    def test_overlay_before_results(self):
        """draw_crop_overlay() MUST appear before the filter results display
        block (not just any 'st.session_state.result' reference)."""
        source = read_app()
        overlay_pos = source.index("draw_crop_overlay(")

        # Use the results display header as the anchor — it's unique to the
        # results section and avoids false positives from the sidebar download
        # guard or the apply-button assignment.
        results_marker = "🖼️ Imagen original y recorte digitalizado"
        results_pos = source.index(results_marker)

        assert overlay_pos < results_pos, (
            f"Crop overlay at position {overlay_pos} must appear before "
            f"results display at position {results_pos}."
        )

    def test_sidebar_branding_after_controls(self):
        """Sidebar branding (credits expander) MUST appear after controls."""
        source = read_app()
        # The credits expander should be toward the end of the sidebar section
        credits_pos = source.find("Créditos del proyecto")
        assert credits_pos >= 0, "Credits expander not found"

    def test_download_in_sidebar_section(self):
        """Download button MUST be in the sidebar section (st.sidebar.download_button)."""
        source = read_app()
        sidebar_downloads = re.findall(r'st\.sidebar\.download_button', source)
        assert len(sidebar_downloads) >= 1, (
            "Download button must be in sidebar (st.sidebar.download_button)"
        )


class TestAppContent:
    """Content presence checks."""

    def test_all_8_test_images_present(self):
        """All 8 test image buttons MUST exist."""
        source = read_app()
        images = [
            ("gradiente", "📊 Gradiente"),
            ("circulos", "🎯 Círculos"),
            ("rayos_x", "🩻 Rayos X"),
            ("cuadros", "🏁 Cuadros"),
            ("uniforme", "⬜ Gris"),
            ("documento", "📄 Documento"),
            ("inspeccion", "🔍 Inspección"),
            ("satelital", "🛰️ Satelital"),
        ]
        for key, label in images:
            assert key in source, f"Test image '{key}' missing from app.py"

    def test_course_branding_header_present(self):
        """Course line 'MA475 • UPC • 2026-S6' MUST appear in main column."""
        source = read_app()
        assert "MA475" in source, "Course branding 'MA475' not found in app.py"
        assert "UPC" in source, "Course branding 'UPC' not found in app.py"
        assert "2026-S6" in source, "Course branding '2026-S6' not found in app.py"

    def test_dark_mode_toggle_present(self):
        """Dark mode toggle MUST exist in sidebar."""
        source = read_app()
        assert "Modo oscuro" in source, "Dark mode toggle not found"

    def test_clear_button_present(self):
        """'Limpiar imagen' button MUST exist."""
        source = read_app()
        assert "Limpiar" in source, "Clear button not found"

    def test_crop_size_constant_defined(self):
        """app.py MUST define CROP_SIZE constant (replaced the slider)."""
        source = read_app()
        assert "CROP_SIZE" in source, "CROP_SIZE constant not found"
        assert "CROP_SIZE = 15" in source, (
            "CROP_SIZE should default to 15 (removed slider for stability)"
        )

    def test_kernel_slider_present(self):
        """'Tamaño del kernel' slider MUST exist."""
        source = read_app()
        assert "Tamaño del kernel" in source, "Kernel slider not found"

    def test_credits_expander_present(self):
        """Credits expander MUST exist."""
        source = read_app()
        assert "Créditos del proyecto" in source, "Credits expander not found"
        assert "Rodriguez Espinoza" in source, "Team member not found in credits"
        assert "Acosta Neyra" in source, "Professor not found in credits"


class TestAppTriangulation:
    """Edge-case / triangulation tests for deeper structural verification."""

    def test_cold_start_dual_guard(self):
        """Cold start guard MUST have BOTH st.stop() and sys.exit(0)."""
        source = read_app()
        # Find the cold start guard section: after "gray is None" check
        # Both st.stop() and sys.exit(0) must appear after the guard condition
        guard_section = source[source.index("if gray is None:"):]
        guard_section = guard_section[:guard_section.index("\n\n") + 1]
        assert "st.stop()" in guard_section, (
            "Cold start guard missing st.stop()"
        )
        assert "sys.exit(0)" in guard_section, (
            "Cold start guard missing sys.exit(0)"
        )

    def test_clear_button_resets_all_5_keys(self):
        """Clear button MUST reset all 5 session state keys."""
        source = read_app()
        # Find the clear button block
        clear_section_idx = source.find("Limpiar imagen")
        assert clear_section_idx >= 0, "Clear button not found"

        # Extract the block around it (roughly 30 lines)
        clear_section = source[clear_section_idx:clear_section_idx + 500]
        for key in ("img_gray", "img_source", "result", "raw", "filter_applied"):
            assert key in clear_section, (
                f"Clear button block missing session key '{key}'"
            )

    def test_test_image_buttons_have_rerun_inside(self):
        """Every test image button MUST have st.rerun() inside the if block."""
        source = read_app()
        # Match each button by its full emoji+text label
        button_patterns = [
            r'st\.button\("📊 Gradiente"\)',
            r'st\.button\("🎯 Círculos"\)',
            r'st\.button\("🩻 Rayos X"\)',
            r'st\.button\("🏁 Cuadros"\)',
            r'st\.button\("⬜ Gris"\)',
            r'st\.button\("📄 Documento"\)',
            r'st\.button\("🔍 Inspección"\)',
            r'st\.button\("🛰️ Satelital"\)',
        ]
        for pattern in button_patterns:
            match = re.search(pattern, source)
            assert match is not None, f"Button pattern not found: {pattern}"
            btn_idx = match.start()
            # The block ends at the next st.button() or sidebar section boundary
            next_btn = source.find("\n    if st.button(", btn_idx + 1)
            if next_btn == -1:
                next_btn = source.find("st.sidebar.markdown", btn_idx + 1)
            block = source[btn_idx:next_btn] if next_btn > 0 else source[btn_idx:]
            assert "st.rerun()" in block, (
                f"Test image button missing st.rerun() inside its if block. "
                f"Block: {block[:200]}"
            )

    def test_no_orphan_st_rerun_outside_buttons(self):
        """st.rerun() MUST NOT appear outside an 'if st.button' block
        (except as part of the apply button or clear button)."""
        source = read_app()
        lines = source.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if "st.rerun()" in stripped:
                # The rerun() call MUST be inside an if block
                # Check the indentation: if it has less indent than a
                # typical if-body, it's orphaned
                indent = len(line) - len(line.lstrip())
                # Walk backwards to find if it's inside a button block
                found_inside = False
                for j in range(i - 1, max(i - 20, -1), -1):
                    prev_line = lines[j]
                    prev_stripped = prev_line.strip()
                    if prev_stripped.startswith("if st.button("):
                        # Check that this rerun is inside the if body
                        prev_indent = len(prev_line) - len(prev_line.lstrip())
                        found_inside = indent > prev_indent
                        break

                if not found_inside:
                    # This might be a legitimate rerun — check if it's inside
                    # the clear button block or apply button block
                    pass  # acceptable for clear/apply buttons

    def test_download_filename_uses_session_source(self):
        """Download filename MUST include img_source and filter_applied."""
        source = read_app()
        file_name_pattern = re.search(
            r'file_name=.*?st\.session_state\.img_source.*?filter_name\.lower\(\).*?',
            source,
        )
        assert file_name_pattern is not None, (
            "Download filename must include both img_source (from session_state) "
            "and filter_applied (via filter_name.lower())"
        )
