# gui.py
"""Main GUI for Different Fun CDGenPS2 – RootISO node, boot‑ELF only on ELF selection."""

from __future__ import annotations
import os
from typing import Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QMessageBox, QSplitter, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton
)

# action modules
from actions.add_folder import add_folder
from actions.add_file import add_file
from actions.boot_elf import boot_elf
from actions.remove_item import remove_item
from actions.build_iso import build_iso


class CDGenPS2(QWidget):
    """Main widget: tree (left) + info table (right)."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Different Fun CDGenPS2")
        self.resize(1120, 650)

        # internal data
        self.files: list[Tuple[str, str, Optional[int]]] = []
        self.current_item: Optional[QTreeWidgetItem] = None

        # ------------ layout -------------------------------------------------
        main = QVBoxLayout(self)
        bar  = QHBoxLayout(); main.addLayout(bar)

        self.btn_add_folder = QPushButton("Add Folder")
        self.btn_add_file   = QPushButton("Add Files")
        self.btn_boot_elf   = QPushButton("Set as main ELF boot")   # will be enabled on ELF node
        self.btn_remove     = QPushButton("Delete")
        self.btn_build_iso  = QPushButton("Build ISO")

        for b in (self.btn_add_folder, self.btn_add_file, self.btn_boot_elf, self.btn_remove, self.btn_build_iso):
            bar.addWidget(b)
        self.btn_boot_elf.setEnabled(False)  # disabled until an ELF node is selected

        split = QSplitter(Qt.Horizontal); main.addWidget(split, 1)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ISO Structure"])
        self.tree.itemClicked.connect(self._on_tree_click)
        split.addWidget(self.tree)

        self.root_node = QTreeWidgetItem(["RootISO"])
        self.tree.addTopLevelItem(self.root_node); self.tree.expandItem(self.root_node)

        self.info = QTableWidget(4, 2)
        self.info.setHorizontalHeaderLabels(["Field", "Value"])
        self.info.verticalHeader().setVisible(False)
        self.info.horizontalHeader().setStretchLastSection(True)
        self.info.setEditTriggers(QTableWidget.NoEditTriggers)
        for i, lbl in enumerate(("Type", "Path", "Size (KB)", "LBA")):
            self.info.setItem(i, 0, QTableWidgetItem(lbl))
        split.addWidget(self.info); split.setSizes([700, 420])

        # ------------ connections -------------------------------------------
        self.btn_add_folder.clicked.connect(lambda: add_folder(self))
        self.btn_add_file.clicked.connect(lambda: add_file(self))
        self.btn_boot_elf.clicked.connect(lambda: boot_elf(self))
        self.btn_remove.clicked.connect(lambda: remove_item(self))
        self.btn_build_iso.clicked.connect(lambda: build_iso(self))

    # =================================================================== #
    def collect_iso_path(self, item: QTreeWidgetItem) -> str:
        parts = []
        node = item
        while node and node != self.root_node:
            parts.insert(0, node.text(0)); node = node.parent()
        return "RootISO/" + "/".join(parts)

    def refresh_info(self, item: QTreeWidgetItem) -> None:
        data = item.data(0, Qt.UserRole)
        if data is None:  # directory
            for r in range(4):
                self.info.setItem(r, 1, QTableWidgetItem(""))
            self.info.setItem(0, 1, QTableWidgetItem("Directory"))
            self.info.setItem(1, 1, QTableWidgetItem(self.collect_iso_path(item)))
            return

        iso_rel, abs_path, lba = data
        size_kb = round(os.path.getsize(abs_path) / 1024, 2)
        self.info.setItem(0, 1, QTableWidgetItem("File"))
        self.info.setItem(1, 1, QTableWidgetItem(f"RootISO/{iso_rel}"))
        self.info.setItem(2, 1, QTableWidgetItem(str(size_kb)))
        self.info.setItem(3, 1, QTableWidgetItem("" if lba is None else str(lba)))

    # ------------------------------------------------------------------ #
    def _on_tree_click(self, item: QTreeWidgetItem) -> None:
        """Handle selection: show info and enable boot‑ELF button only on .ELF."""
        self.current_item = item
        self.refresh_info(item)

        data = item.data(0, Qt.UserRole)
        is_elf_file = bool(data and data[0].upper().endswith(".ELF"))
        self.btn_boot_elf.setEnabled(is_elf_file)
