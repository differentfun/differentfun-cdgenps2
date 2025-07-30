# actions/build_iso.py
"""Build the PlayStation 2 ISO image *with* user‑interface feedback."""

from __future__ import annotations
import os, traceback
from typing import List, Tuple, Optional, TYPE_CHECKING

from PySide6.QtCore   import QThread, QObject, Signal
from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog

from iso_builder import create_ps2_iso_with_lba

if TYPE_CHECKING:  # pragma: no cover
    from gui import CDGenPS2

# --------------------------------------------------------------------------- #
# Sanity‑check helper  ← NEW
# --------------------------------------------------------------------------- #
def _sanitise_and_sort(
    files: List[Tuple[str, str, Optional[int]]],
) -> List[Tuple[str, str, Optional[int]]]:
    """Validate layout, then return it ordered by LBA / insertion."""
    seen: set[str] = set()
    ordered: List[Tuple[str, str, Optional[int]]] = []

    for iso_rel, abs_path, lba in files:
        if iso_rel in seen:
            raise ValueError(f"Duplicate ISO path: {iso_rel}")
        seen.add(iso_rel)

        if not os.path.isfile(abs_path):
            raise FileNotFoundError(abs_path)

        ordered.append((iso_rel, abs_path, lba))

    # Explicit LBA first (ascending), then the rest in original order
    ordered.sort(key=lambda t: (1 if t[2] is None else 0, t[2] or 0))
    return ordered

# --------------------------------------------------------------------------- #
# Worker thread
# --------------------------------------------------------------------------- #
class _IsoBuildWorker(QObject):
    finished = Signal(str)
    error    = Signal(str)

    def __init__(
        self,
        output_path: str,
        files_with_lba: List[Tuple[str, Optional[int]]],
    ) -> None:
        super().__init__()
        self._output_path   = output_path
        self._files_with_lba = files_with_lba

    def run(self) -> None:  # executed in worker thread
        try:
            create_ps2_iso_with_lba(self._output_path, self._files_with_lba)
        except Exception as exc:  # propagate full traceback
            self.error.emit(f"{exc}\n\n{traceback.format_exc()}")
            return
        self.finished.emit(self._output_path)

# --------------------------------------------------------------------------- #
# GUI entry‑point
# --------------------------------------------------------------------------- #
def build_iso(gui: "CDGenPS2") -> None:  # noqa: D401
    """Collect files from GUI, validate, and build the ISO in a thread."""
    if not gui.files:
        QMessageBox.warning(gui, "No content",
                            "Add at least one file before building the ISO.")
        return

    # 1) validate & sort
    try:
        sorted_files = _sanitise_and_sort(gui.files)
    except Exception as err:
        QMessageBox.critical(gui, "Invalid layout", str(err))
        return

    # 2) choose output path
    save_path, _ = QFileDialog.getSaveFileName(
        gui, "Save ISO as…", "output.iso", "ISO (*.iso)"
    )
    if not save_path:
        return

    # 3) progress dialog + worker thread
    progress = QProgressDialog("Building ISO…", "Cancel", 0, 0, gui)
    progress.setWindowModality(progress.WindowModal)
    progress.setMinimumDuration(0)
    progress.setValue(0)  # indeterminate

    worker = _IsoBuildWorker(
        save_path,
        [(abs_path, lba) for _iso_rel, abs_path, lba in sorted_files],
    )
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)

    # success
    worker.finished.connect(
        lambda path: (
            progress.close(),
            QMessageBox.information(gui, "Success",
                                    f"ISO successfully created:\n{path}"),
            thread.quit(), thread.wait()
        )
    )
    # error
    worker.error.connect(
        lambda msg: (
            progress.close(),
            QMessageBox.critical(gui, "Build error", msg),
            thread.quit(), thread.wait()
        )
    )
    # cancellation
    progress.canceled.connect(
        lambda: (thread.requestInterruption(),
                 progress.setLabelText("Cancelling…"))
    )

    # 4) launch
    thread.start()
    progress.exec()
