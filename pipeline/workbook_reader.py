"""Read project rows from the Excel workbook."""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from ooxml import NS, cell_text, shared_strings, sheet_paths, split_ref

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XLSX = REPO_ROOT / "sources" / "Public Invention Projects.xlsx"
DEFAULT_SHEETS = {"Projects", "Shortlist"}


def read_project_rows(xlsx: Path = DEFAULT_XLSX, sheets: set[str] = DEFAULT_SHEETS) -> list[dict]:
    """Read project name and link cells from selected workbook tabs."""
    records = []

    # Open the workbook as a zip archive.
    with zipfile.ZipFile(xlsx) as z:
        # Shared strings are Excel's string table for normal text cells.
        strings = shared_strings(z)

        # Walk all sheets, but only parse the tabs requested by the caller.
        for sheet_name, target in sheet_paths(z).items():
            if sheet_name not in sheets:
                continue
            records.extend(read_sheet(z, target, strings, sheet_name))
    return records


def read_sheet(z: zipfile.ZipFile, target: str, strings: list[str], sheet_name: str) -> list[dict]:
    """Read project rows from one worksheet XML file."""
    # Build a sparse cell grid keyed by (row_number, column_number).
    grid, max_row, max_col = read_grid(z, target, strings)

    # Header matching is prefix-based because some headers are long sentences.
    headers = {grid.get((1, col), "").strip().lower(): col for col in range(1, max_col + 1)}
    project_col = find_header(headers, "project", "name")
    link_col = find_header(headers, "github", "link")

    # If a sheet does not have project/link columns, it is not a source sheet.
    if not project_col or not link_col:
        return []

    # Convert each non-empty project row into the normalized record shape.
    records = []
    for row in range(2, max_row + 1):
        project = grid.get((row, project_col), "").strip()
        if project:
            records.append({
                "_sheet": sheet_name,
                "_row": row,
                "project": project,
                "link": grid.get((row, link_col), "").strip(),
            })
    return records


def read_grid(z: zipfile.ZipFile, target: str, strings: list[str]) -> tuple[dict, int, int]:
    """Convert worksheet XML cells into a sparse grid dictionary."""
    worksheet = ET.fromstring(z.read(target))
    grid, max_row, max_col = {}, 0, 0

    # Excel stores cells sparsely; blank cells are simply absent from XML.
    for cell in worksheet.findall(".//m:sheetData/m:row/m:c", NS):
        col, row = split_ref(cell.attrib.get("r", ""))
        if not col:
            continue

        # Track dimensions so callers can iterate header/data ranges.
        max_row = max(max_row, row)
        max_col = max(max_col, col)
        grid[(row, col)] = cell_text(cell, strings).strip()
    return grid, max_row, max_col


def find_header(headers: dict[str, int], *candidates: str) -> int | None:
    """Find a column whose header equals or starts with any candidate."""
    for header, col in headers.items():
        if any(header == candidate or header.startswith(candidate) for candidate in candidates):
            return col
    return None
