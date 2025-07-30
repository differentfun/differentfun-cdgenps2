# actions/add_folder.py
"""Add an entire directory tree to the ISO layout, with ISO‑9660 name checks."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Tuple

from PySide6.QtWidgets import QFileDialog, QMessageBox, QTreeWidgetItem
from PySide6.QtCore import Qt

if TYPE_CHECKING:  # pragma: no cover
    from gui import CDGenPS2  # type‑hints only

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

_VALID_CHARS = re.compile(r"[^A-Z0-9_.$]")


def _norm_iso_name(name: str) -> str:
    name = name.upper()
    name = _VALID_CHARS.sub("_", name)
    if len(name) <= 31:
        return name

    base, dot, ext = name.partition(".")
    trunc = (31 - len(dot) - len(ext)) if dot else 31
    return base[:trunc] + (dot + ext if dot else "")


def _iter_dir(root: Path) -> Iterator[Tuple[Path, str]]:
    """Yield (absolute_path, iso_relative_path) for every file under *root*."""
    for abs_path in root.rglob("*"):
        if abs_path.is_file():
            rel_parts = [ _norm_iso_name(p.name) for p in abs_path.relative_to(root).parts ]
            yield abs_path, "/".join(rel_parts)


# --------------------------------------------------------------------------- #
# Public entry‑point
# --------------------------------------------------------------------------- #

def add_folder(gui: "CDGenPS2") -> None:  # noqa: D401
    dir_path = QFileDialog.getExistingDirectory(gui, "Select folder to add")
    if not dir_path:
        return

    root = Path(dir_path)
    new_nodes = []

    for abs_path, iso_rel in _iter_dir(root):
        # Skip duplicates
        if any(entry[0] == iso_rel for entry in gui.files):
            continue

        # Build tree hierarchy node‑by‑node
        parent = gui.root_node
        parts = iso_rel.split("/")
        for depth, part in enumerate(parts):
            child = next(
                (parent.child(i) for i in range(parent.childCount()) if parent.child(i).text(0) == part),
                None,
            )
            if child is None:
                child = QTreeWidgetItem([part])
                parent.addChild(child)
            parent = child

            if depth == len(parts) - 1:  # leaf → file node
                parent.setData(0, Qt.UserRole, (iso_rel, str(abs_path), None))
                new_nodes.append(parent)

        gui.files.append((iso_rel, str(abs_path), None))

    if not new_nodes:
        QMessageBox.information(gui, "Nothing added", "All items already exist in the ISO.")
        return

    gui.tree.setCurrentItem(new_nodes[0])
    QMessageBox.information(gui, "Folder added", f"Imported {len(new_nodes)} file(s) from {root.name}.")
