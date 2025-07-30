# actions/add_file.py
"""Add a single file to the ISO layout, enforcing ISO‑9660 naming rules."""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Tuple

from PySide6.QtWidgets import QFileDialog, QMessageBox, QTreeWidgetItem
from PySide6.QtCore import Qt

if TYPE_CHECKING:  # pragma: no cover
    from gui import CDGenPS2  # type‑hints only

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

_VALID_CHARS = re.compile(r"[^A-Z0-9_.$]")


def _norm_iso_name(name: str) -> Tuple[str, bool]:
    """Return a valid ISO‑9660 (level 2) file name, flagging if it changed."""
    original = name
    name = name.upper()
    name = _VALID_CHARS.sub("_", name)

    if len(name) <= 31:
        return name, name != original.upper()

    # Preserve extension, truncate base
    base, dot, ext = name.partition(".")
    trunc = (31 - len(dot) - len(ext)) if dot else 31
    name = base[:trunc] + (dot + ext if dot else "")
    return name, True


# --------------------------------------------------------------------------- #
# Public entry‑point
# --------------------------------------------------------------------------- #

def add_file(gui: "CDGenPS2") -> None:
    file_paths, _ = QFileDialog.getOpenFileNames(
        gui, "Select file(s) to add", "", "All files (*)"
    )
    if not file_paths:
        return

    added = 0
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        iso_name, changed = _norm_iso_name(file_name)

        if any(entry[0] == iso_name for entry in gui.files):
            continue  # skip duplicates silently

        if changed:
            QMessageBox.information(
                gui,
                "Name adjusted",
                f"The file name was adapted for ISO‑9660:\n{file_name} → {iso_name}",
            )

        node = QTreeWidgetItem([iso_name])
        node.setData(0, Qt.UserRole, (iso_name, file_path, None))
        gui.root_node.addChild(node)

        gui.files.append((iso_name, file_path, None))
        added += 1

    if added:
        gui.tree.setCurrentItem(node)
    else:
        QMessageBox.information(gui, "No files added", "All selected files were duplicates.")
