# actions/remove_item.py
"""Remove a file or directory (recursively) from the ISO tree **and** update
``gui.files`` accordingly.

Key improvements over the previous implementation
-------------------------------------------------
* **Single pass filter → O(N)** – All ISO‑relative paths to delete are first
  collected, then ``gui.files`` is filtered once.  This avoids repeatedly
  rebuilding the list during deep recursions.
* **Robust traversal** – Uses a DFS helper that does *not* rely on the
  current child index after modifications, making the code future‑proof if
  we later decide to prune the GUI tree inside the recursion.
* **UX polish** – Clears the info panel, resets the current selection, and
  disables the *Boot ELF* button once the deletion is complete.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Set

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QTreeWidgetItem, QTableWidgetItem

if TYPE_CHECKING:  # pragma: no cover
    from gui import CDGenPS2  # type‑hints only

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _collect_iso_paths(item: QTreeWidgetItem, acc: Set[str]) -> None:
    """Depth‑first search that stores every file ISO path found under *item*."""
    data = item.data(0, Qt.UserRole)
    if data:
        acc.add(data[0])  # iso‑relative path

    for idx in range(item.childCount()):
        _collect_iso_paths(item.child(idx), acc)

# --------------------------------------------------------------------------- #
# Public entry‑point
# --------------------------------------------------------------------------- #

def remove_item(gui: "CDGenPS2") -> None:  # noqa: D401
    item = getattr(gui, "current_item", None)
    if item is None:
        QMessageBox.warning(gui, "No selection", "Select an item to delete.")
        return

    if item is gui.root_node:
        QMessageBox.information(gui, "RootISO", "The RootISO node cannot be removed.")
        return

    if (
        QMessageBox.question(
            gui,
            "Confirm delete",
            "Remove this item (and its children) from the ISO layout?",
            QMessageBox.Yes | QMessageBox.No,
        )
        != QMessageBox.Yes
    ):
        return

    # 1) Gather all ISO paths to drop ------------------------------------------------
    paths_to_remove: Set[str] = set()
    _collect_iso_paths(item, paths_to_remove)

    # 2) Filter gui.files in a single pass ------------------------------------------
    gui.files = [f for f in gui.files if f[0] not in paths_to_remove]

    # 3) Detach the node from the tree ---------------------------------------------
    parent = item.parent()
    if parent is not None:
        parent.removeChild(item)

    gui.current_item = None  # reset selection

    # 4) Clear the info panel -------------------------------------------------------
    for r in range(4):
        gui.info.setItem(r, 1, QTableWidgetItem(""))

    gui.btn_boot_elf.setEnabled(False)
