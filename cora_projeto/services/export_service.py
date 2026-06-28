"""Utilitarios de exportacao (arquivos de imagem e planilha XLSX sem dependencia externa)."""

import hashlib
import math
import re
from pathlib import Path
import zipfile
from xml.sax.saxutils import escape as xml_escape

import cv2
import numpy as np


def safe_filename(name: str, max_len: int = 120) -> str:
    """Normaliza nomes para uso seguro em caminhos, com truncamento deterministico."""
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    clean = re.sub(r"_+", "_", clean)
    if not clean:
        return "resultado"
    if len(clean) <= max_len:
        return clean
    digest = hashlib.sha1(clean.encode("utf-8")).hexdigest()[:10]
    head_len = max(1, max_len - 11)
    head = clean[:head_len].rstrip("._-")
    if not head:
        head = "resultado"
    return f"{head}_{digest}"


def write_image_file(path: Path, image: np.ndarray) -> bool:
    """Grava imagem com suporte a caminhos Unicode no Windows."""
    suffix = path.suffix.lower() or ".png"
    ok, encoded = cv2.imencode(suffix, image)
    if not ok:
        return False
    try:
        encoded.tofile(str(path))
    except Exception:
        return False
    return True


def excel_col_name(col_idx_1based: int) -> str:
    """Converte indice 1-based para nome de coluna Excel (A, B, ..., AA...)."""
    idx = int(col_idx_1based)
    if idx <= 0:
        return "A"
    out = ""
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        out = chr(65 + rem) + out
    return out


def excel_sheet_name(base: str, used_lower: set[str]) -> str:
    """Gera nome de planilha valido e unico dentro do limite de 31 caracteres."""
    name = re.sub(r"[\\/*?:\[\]]+", "_", str(base)).strip()
    if not name:
        name = "Grupo"
    name = name[:31]

    cand = name
    suffix = 2
    while cand.lower() in used_lower:
        tail = f"_{suffix}"
        head = name[: max(1, 31 - len(tail))]
        cand = f"{head}{tail}"
        suffix += 1
    used_lower.add(cand.lower())
    return cand


def excel_cell_xml(row_idx_1based: int, col_idx_1based: int, value: object) -> str:
    """Serializa uma celula no formato XML de planilha OpenXML."""
    if value is None or value == "":
        return ""

    ref = f"{excel_col_name(col_idx_1based)}{int(row_idx_1based)}"
    if isinstance(value, (np.integer, int)) and not isinstance(value, bool):
        return f'<c r="{ref}"><v>{int(value)}</v></c>'
    if isinstance(value, (np.floating, float)):
        fval = float(value)
        if math.isfinite(fval):
            return f'<c r="{ref}"><v>{fval:.8f}</v></c>'

    sval = xml_escape(str(value))
    return f'<c r="{ref}" t="inlineStr"><is><t>{sval}</t></is></c>'


def excel_sheet_xml(headers: list[str], rows: list[list[object]]) -> str:
    """Monta o XML completo de uma worksheet com cabecalho e linhas de dados."""
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        "<sheetData>",
    ]

    header_cells = []
    for col_idx, value in enumerate(headers, start=1):
        cell_xml = excel_cell_xml(1, col_idx, value)
        if cell_xml:
            header_cells.append(cell_xml)
    xml_lines.append(f'<row r="1">{"".join(header_cells)}</row>')

    row_idx = 2
    for row in rows:
        body_cells = []
        for col_idx, value in enumerate(row, start=1):
            cell_xml = excel_cell_xml(row_idx, col_idx, value)
            if cell_xml:
                body_cells.append(cell_xml)
        if body_cells:
            xml_lines.append(f'<row r="{row_idx}">{"".join(body_cells)}</row>')
        else:
            xml_lines.append(f'<row r="{row_idx}"/>')
        row_idx += 1

    xml_lines.append("</sheetData>")
    xml_lines.append("</worksheet>")
    return "".join(xml_lines)


def write_results_excel(xlsx_path: Path, rows: list[dict[str, object]], group_order: list[str]) -> None:
    """Escreve a planilha final em .xlsx usando zip + XML (sem openpyxl)."""
    # PT: Estrutura alinhada ao Exemplo_planilha_resultados.xlsx: primeira coluna com o identificador do grupo (sem cabecalho) e metricas em 0h/24h/48h com fechamento percentual.
    # EN: Structure aligned with Exemplo_planilha_resultados.xlsx: first column with the group identifier (without a header), followed by 0h/24h/48h metrics and percentage closure.
    headers = [
        "",
        "C- i 0h (pixel)",
        "C- i 24h (pixel)",
        "C- i 48h (pixel)",
        "Fechamento 0h - 24h (%)",
        "Fechamento 0h - 48h (%)",
    ]

    by_group_time: dict[tuple[str, str], dict[str, object]] = {}
    for row in rows:
        g = str(row.get("grupo", ""))
        t = str(row.get("tempo", "")).lower()
        by_group_time[(g, t)] = row

    sheet_rows: list[list[object]] = []
    for group_key in group_order:
        row_0h = by_group_time.get((group_key, "0h"), {})
        row_24h = by_group_time.get((group_key, "24h"), {})
        row_48h = by_group_time.get((group_key, "48h"), {})

        parts = str(group_key).split(maxsplit=1)
        group_display = parts[1] if (len(parts) == 2 and parts[0].lower() in {"i", "ni"}) else str(group_key)

        sheet_rows.append(
            [
                group_display,
                row_0h.get("area_auto_px", ""),
                row_24h.get("area_auto_px", ""),
                row_48h.get("area_auto_px", ""),
                row_24h.get("fechamento_area_pct_vs_0h", ""),
                row_48h.get("fechamento_area_pct_vs_0h", ""),
            ]
        )

    sheets: list[tuple[str, list[str], list[list[object]]]] = [("Plan1", headers, sheet_rows)]

    used_sheet_names: set[str] = set()
    sheet_names: list[str] = []
    for raw_name, _, _ in sheets:
        safe_name = excel_sheet_name(raw_name, used_sheet_names)
        sheet_names.append(safe_name)

    content_types = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for idx in range(1, len(sheets) + 1):
        content_types.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    content_types.append("</Types>")
    content_types_xml = "".join(content_types)

    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )

    workbook_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        "<sheets>",
    ]
    for idx, sheet_name in enumerate(sheet_names, start=1):
        workbook_lines.append(
            f'<sheet name="{xml_escape(sheet_name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        )
    workbook_lines.extend(["</sheets>", "</workbook>"])
    workbook_xml = "".join(workbook_lines)

    workbook_rels_lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
    ]
    for idx in range(1, len(sheets) + 1):
        workbook_rels_lines.append(
            f'<Relationship Id="rId{idx}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{idx}.xml"/>'
        )
    workbook_rels_lines.append("</Relationships>")
    workbook_rels_xml = "".join(workbook_rels_lines)

    with zipfile.ZipFile(str(xlsx_path), mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)

        for idx, (_raw_name, headers, sheet_rows) in enumerate(sheets, start=1):
            sheet_xml = excel_sheet_xml(headers=headers, rows=sheet_rows)
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", sheet_xml)

