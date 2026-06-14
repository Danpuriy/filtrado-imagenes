# Course Branding Specification

## Purpose

Display visible course attribution (MA475 • UPC • 2026-S6) in the application header, sidebar footer, and an expandable credits panel with full project metadata.

## Requirements

### Requirement: Header course line

The system MUST render a header line "MA475 • UPC • 2026-S6" immediately below the main application title.

#### Scenario: Header line visible on page load

- GIVEN the application loads
- WHEN the main title is rendered
- THEN a line "MA475 • UPC • 2026-S6" appears directly below the title

### Requirement: Sidebar footer with course info

The system MUST display a persistent caption in the sidebar footer containing the course attribution line.

#### Scenario: Sidebar footer visible

- GIVEN the sidebar is rendered
- WHEN the user scrolls to the bottom of the sidebar
- THEN "MA475 • UPC • 2026-S6" is visible as a caption

### Requirement: Credits expander in sidebar

The system MUST provide an expander labeled "ℹ️ Créditos del proyecto" in the sidebar. When expanded, it MUST display:
- Course: MA475 - Matemática Computacional
- Institution: UPC - Universidad Peruana de Ciencias Aplicadas
- Integrantes: Chavez Giraldo, Andrei Gabriel; Romero Veliz, Matthias Alonso; Escalante Rojas, Rogger Junior; Zea Diaz, Jesús Enrique; Rodriguez Espinoza, Daniel Kevin
- Profesor: Jesús Manuel Acosta Neyra
- Período: 2026 (Semana 6 / primera revisión)

#### Scenario: Credits expander shows all metadata

- GIVEN the sidebar is rendered
- WHEN the user clicks "ℹ️ Créditos del proyecto"
- THEN the expander opens showing all 5 members, professor, course, institution, and period

#### Scenario: Credits expander collapses by default

- GIVEN the application loads
- WHEN the sidebar renders
- THEN the "ℹ️ Créditos del proyecto" expander is collapsed

## Validation Criteria

- [ ] Header line "MA475 • UPC • 2026-S6" visible under main title
- [ ] Sidebar footer shows course line persistently
- [ ] Expander "ℹ️ Créditos del proyecto" present in sidebar
- [ ] Expander displays all 5 integrantes
- [ ] Expander displays professor name
- [ ] Expander displays course, institution, period
- [ ] Expander collapsed by default