"""Write computed columns back into the Excel workbook."""
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from ooxml import NS, cell_text, ensure_cell, set_text, shared_strings, sheet_paths, split_ref


def write_computed_columns(xlsx: Path, records: list[dict], columns: dict[str, str]) -> None:
    """Write computed fields into workbook columns."""
    # Key rows by original sheet name and row number so output lands in place.
    updates = {(record["_sheet"], record["_row"]): record for record in records}

    # Write to a temporary workbook first, then replace the original.
    tmp = xlsx.with_suffix(xlsx.suffix + ".tmp")

    with zipfile.ZipFile(xlsx, "r") as zin:
        # Shared strings are needed to read existing header text.
        strings = shared_strings(zin)

        # rewritten maps workbook XML paths to edited XML bytes.
        rewritten = {}

        # Visit every worksheet, but only rewrite sheets with changed rows.
        for sheet_name, target in sheet_paths(zin).items():
            worksheet = ET.fromstring(zin.read(target))
            if update_sheet(worksheet, strings, sheet_name, updates, columns):
                rewritten[target] = ET.tostring(worksheet, encoding="utf-8", xml_declaration=True)

        # Copy every original zip entry, substituting edited worksheet XML.
        with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                zout.writestr(item, rewritten.get(item.filename, zin.read(item.filename)))

    # Atomically replace the workbook with the rewritten copy.
    shutil.move(tmp, xlsx)


def update_sheet(
    worksheet: ET.Element,
    strings: list[str],
    sheet_name: str,
    updates: dict[tuple[str, int], dict],
    columns: dict[str, str],
) -> bool:
    """Update one worksheet XML tree and report whether it changed."""
    # Find the worksheet's row container.
    sheet_data = worksheet.find("m:sheetData", NS)
    if sheet_data is None:
        return False

    # Index row elements by their Excel row number.
    rows = {int(row.attrib["r"]): row for row in sheet_data.findall("m:row", NS)}

    # Row 1 is expected to contain headers.
    header = rows.get(1)
    if header is None:
        return False

    # Ensure the computed output columns exist before writing data rows.
    target_cols = ensure_headers(header, strings, columns.keys())
    changed = False

    # Update only rows that came from the reader; unrelated rows are untouched.
    for row_num, row in rows.items():
        record = updates.get((sheet_name, row_num))
        if not record:
            continue

        # Write each computed field into its matching output column.
        for header_name, field in columns.items():
            set_text(ensure_cell(row, target_cols[header_name]), str(record.get(field) or ""))
        changed = True
    return changed


def ensure_headers(row: ET.Element, strings: list[str], headers: list[str]) -> dict[str, int]:
    """Return output column positions, adding missing headers if needed."""
    # Read existing header cells first so reruns reuse the same columns.
    existing, max_col = read_header_columns(row, strings)
    result = {}

    # Add any missing computed headers to the right of existing named columns.
    for header in headers:
        col = existing.get(header.lower())
        if col is None:
            max_col += 1
            col = max_col
            set_text(ensure_cell(row, col), header)
        result[header] = col
    return result


def read_header_columns(row: ET.Element, strings: list[str]) -> tuple[dict[str, int], int]:
    """Read header text -> column number from the header row."""
    headers, max_col = {}, 0
    for cell in row.findall("m:c", NS):
        col, _ = split_ref(cell.attrib.get("r", ""))
        if not col:
            continue

        # Empty headers are ignored; max_col tracks only named columns.
        text = cell_text(cell, strings).strip()
        if text:
            headers[text.lower()] = col
            max_col = max(max_col, col)
    return headers, max_col
