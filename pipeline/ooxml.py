"""Minimal OOXML helpers for .xlsx files.

The pipeline avoids third-party dependencies, so it edits the workbook as XML
inside the .xlsx zip. Higher-level workbook code should own row/column meaning.
"""
import zipfile
import xml.etree.ElementTree as ET

# SpreadsheetML namespace used by worksheet XML files.
M_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

# Package relationship namespace used to map workbook sheets to XML files.
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

# Office relationship namespace used for sheet relationship ids.
OFFICE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# Prefix map used by ElementTree XPath calls.
NS = {"m": M_NS}

# Preserve the default SpreadsheetML namespace when writing XML back.
ET.register_namespace("", M_NS)


def sheet_paths(z: zipfile.ZipFile) -> dict[str, str]:
    """Return worksheet display name -> XML path inside the workbook zip."""
    # workbook.xml lists sheets by name and relationship id.
    workbook = ET.fromstring(z.read("xl/workbook.xml"))

    # workbook.xml.rels maps relationship ids to actual worksheet XML paths.
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{REL_NS}}}Relationship")
    }

    # Build a direct lookup so callers can read a sheet by visible tab name.
    paths = {}
    for sheet in workbook.findall("m:sheets/m:sheet", NS):
        target = rel_targets[sheet.attrib[f"{{{OFFICE_REL}}}id"]]

        # Relationship targets are sometimes relative to xl/.
        paths[sheet.attrib["name"]] = target if target.startswith("xl/") else "xl/" + target
    return paths


def shared_strings(z: zipfile.ZipFile) -> list[str]:
    """Read Excel's shared string table."""
    # Workbooks with only inline strings may not have sharedStrings.xml.
    if "xl/sharedStrings.xml" not in z.namelist():
        return []

    # Shared strings are stored as rich text runs; join all text nodes.
    root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    return [
        "".join((text.text or "") for text in item.findall(".//m:t", NS))
        for item in root.findall("m:si", NS)
    ]


def cell_text(cell: ET.Element, strings: list[str]) -> str:
    """Return a cell's displayed text value."""
    # Normal cells store their value under <v>.
    value = cell.find("m:v", NS)

    # t="s" means <v> is an index into sharedStrings.xml.
    if cell.attrib.get("t") == "s" and value is not None and value.text is not None:
        return strings[int(value.text)]

    # t="inlineStr" means the text lives directly inside the cell.
    if cell.attrib.get("t") == "inlineStr":
        inline = cell.find("m:is", NS)
        return "".join((text.text or "") for text in inline.findall(".//m:t", NS)) if inline is not None else ""

    # Numeric/plain cells can be returned directly from <v>.
    return value.text if value is not None and value.text is not None else ""


def split_ref(ref: str) -> tuple[int | None, int | None]:
    """Convert an Excel cell reference like C12 into (3, 12)."""
    # Separate column letters from row digits.
    letters = "".join(ch for ch in ref if ch.isalpha())
    digits = "".join(ch for ch in ref if ch.isdigit())
    if not letters or not digits:
        return None, None

    # Convert base-26 letters into a 1-based column number.
    col = 0
    for ch in letters:
        col = col * 26 + ord(ch.upper()) - 64
    return col, int(digits)


def col_name(idx: int) -> str:
    """Convert a 1-based column number into Excel letters."""
    name = ""

    # Excel columns are base-26 but without a zero digit.
    while idx:
        idx, rem = divmod(idx - 1, 26)
        name = chr(65 + rem) + name
    return name


def ensure_cell(row: ET.Element, col: int) -> ET.Element:
    """Return an existing cell in a row, or create it in column order."""
    # Build the Excel cell reference, for example column 14 in row 2 is N2.
    ref = f"{col_name(col)}{row.attrib['r']}"

    # Reuse an existing cell if one is already present.
    cells = row.findall("m:c", NS)
    for cell in cells:
        existing_col, _ = split_ref(cell.attrib.get("r", ""))
        if existing_col == col:
            return cell

    # Create a new blank cell.
    new_cell = ET.Element(f"{{{M_NS}}}c", {"r": ref})

    # Insert before the next higher column so Excel sees cells in normal order.
    for pos, cell in enumerate(cells):
        existing_col, _ = split_ref(cell.attrib.get("r", ""))
        if existing_col and existing_col > col:
            row.insert(pos, new_cell)
            return new_cell

    # Append if this is now the rightmost cell in the row.
    row.append(new_cell)
    return new_cell


def set_text(cell: ET.Element, value: str) -> None:
    """Replace a cell's contents with inline text."""
    # Remove any old <v>, <is>, or formula children.
    for child in list(cell):
        cell.remove(child)

    # Remove the previous cell type before setting the new representation.
    cell.attrib.pop("t", None)

    # Empty string means leave the cell blank.
    if not value:
        return

    # Inline strings keep this writer simple and avoid editing sharedStrings.xml.
    cell.attrib["t"] = "inlineStr"
    inline = ET.SubElement(cell, f"{{{M_NS}}}is")
    ET.SubElement(inline, f"{{{M_NS}}}t").text = value
