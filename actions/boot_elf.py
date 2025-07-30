# actions/boot_elf.py
"""Set the *selected* ELF as default bootstrap for PlayStation 2 images.

The action performs four steps:
1. **Validate selection** – The user must have highlighted an ``*.ELF`` file
   in the ISO tree.
2. **Generate `SYSTEM.CNF`** in a *temporary* directory to avoid cluttering
   the working folder.
3. **Update the GUI tree and `gui.files` list** – Any previous `SYSTEM.CNF`
   entry is removed, then the fresh one (fixed at LBA 12231) is inserted
   under the *RootISO* node and appended to ``gui.files``.
4. **Focus feedback** – Highlights the new node and shows a confirmation
   message.

Limitations
-----------
The LBA is hard‑wired to *12231*, matching the convention used by
CDGenPS2 and understood by the PS2 ROM.  If you later introduce a manual
LBA editor, make sure to prevent placing any file at sectors below that
value once *SYSTEM.CNF* has been created.
"""

from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QTreeWidgetItem

if TYPE_CHECKING:  # pragma: no cover
    from gui import CDGenPS2

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

CNF_NAME: str = "SYSTEM.CNF"
CNF_LBA: int = 12231

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _make_cnf_content(iso_path: str) -> str:
    """Return the text for SYSTEM.CNF given an ELF ISO path."""
    elf_path_cnf = iso_path.replace("/", "\\")
    if not elf_path_cnf.endswith(";1"):
        elf_path_cnf += ";1"

    return (
        f"BOOT2=cdrom0:\\{elf_path_cnf}\n"
        "VER=1.00\n"
        "VMODE=NTSC\n"
    )


def _write_temp_cnf(content: str) -> str:
    """Write *content* to a temporary file and return its absolute path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".CNF", prefix="syscnf_")
    with tmp:
        tmp.write(content.encode("ascii"))
    return tmp.name


# --------------------------------------------------------------------------- #
# Public entry‑point
# --------------------------------------------------------------------------- #

def boot_elf(gui: "CDGenPS2") -> None:  # noqa: D401
    """Create / update *SYSTEM.CNF* for the ELF currently selected in the tree."""

    # ------------------------------------------------------------------
    # 1) Validate selection
    # ------------------------------------------------------------------
    item = getattr(gui, "current_item", None)
    if item is None:
        QMessageBox.warning(gui, "No selection", "Please select an ELF file in the tree.")
        return

    data: Tuple[str, str, int | None] | None = item.data(0, Qt.UserRole)
    if not data or not data[0].upper().endswith(".ELF"):
        QMessageBox.warning(gui, "Invalid selection", "Selected node is not an ELF file.")
        return

    elf_iso, _elf_abs, _elf_lba = data

    # ------------------------------------------------------------------
    # 2) Generate SYSTEM.CNF in a temporary file
    # ------------------------------------------------------------------
    cnf_content = _make_cnf_content(elf_iso.upper())
    cnf_path = _write_temp_cnf(cnf_content)

    # ------------------------------------------------------------------
    # 3) Remove any previous SYSTEM.CNF then insert the new one
    # ------------------------------------------------------------------
    # ---- 3.a) purge gui.files and tree node --------------------------------
    gui.files = [t for t in gui.files if t[0].upper() != CNF_NAME]

    for i in range(gui.root_node.childCount()):
        if gui.root_node.child(i).text(0).upper().startswith(CNF_NAME):
            gui.root_node.removeChild(gui.root_node.child(i))
            break

    # ---- 3.b) create and insert fresh node --------------------------------
    cnf_node = QTreeWidgetItem([f"{CNF_NAME} (LBA: {CNF_LBA})"])
    cnf_node.setData(0, Qt.UserRole, (CNF_NAME, cnf_path, CNF_LBA))
    gui.root_node.insertChild(0, cnf_node)

    gui.files.append((CNF_NAME, cnf_path, CNF_LBA))

    # ------------------------------------------------------------------
    # 4) Final UI feedback
    # ------------------------------------------------------------------
    gui.tree.setCurrentItem(cnf_node)
    gui.refresh_info(cnf_node)

    QMessageBox.information(
        gui,
        "Boot ELF set",
        f"{CNF_NAME} created for {os.path.basename(elf_iso)} at LBA {CNF_LBA}.",
    )
