# actions/build_iso.py
import subprocess, os, logging, threading, traceback
from typing import List, Tuple, Optional
from PySide6.QtCore import QObject, Signal, QThread, Slot, Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox

logger = logging.getLogger("buildiso")
VOLUME_ID = "PS2DISC"

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def _sanitise_and_sort(files: List[Tuple[str, str, Optional[int]]]):
    seen = set()
    ordered = []
    for iso_rel, abs_path, lba in files:
        if iso_rel in seen:
            raise ValueError(f"Duplicate ISO path: {iso_rel}")
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(abs_path)
        seen.add(iso_rel)
        ordered.append((iso_rel, abs_path))
    return ordered

def _build_iso(output_path: str, files: List[Tuple[str, str]]):
    logger.debug("Thread %s – building ISO with genisoimage", threading.get_ident())

    cmd = [
        "genisoimage",
        "-udf",
        "-o", output_path,
        "-iso-level", "1",
        "-pad",
        "-V", VOLUME_ID,
        "-graft-points"
    ]
    for iso_rel, abs_path in files:
        graft = f"/{iso_rel.upper()}={abs_path}"
        cmd.append(graft)
    
    
    logger.info("Running command: %s", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"genisoimage failed with code {result.returncode}")

    logger.info("ISO written to %s", output_path)

# ------------------------------------------------------------------------------
# Worker
# ------------------------------------------------------------------------------

class _IsoBuildWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, out_path: str, files):
        super().__init__()
        self._out = out_path
        self._files = files

    @Slot()
    def run(self):
        try:
            _build_iso(self._out, self._files)
        except Exception as exc:
            self.error.emit(f"{exc}\n\n{traceback.format_exc()}")
        else:
            self.finished.emit(self._out)

# ------------------------------------------------------------------------------
# GUI entry-point
# ------------------------------------------------------------------------------

def build_iso(gui: "CDGenPS2") -> None:
    if not gui.files:
        QMessageBox.warning(gui, "No content", "Add at least one file before building the ISO.")
        return

    try:
        files = _sanitise_and_sort(gui.files)
    except Exception as e:
        QMessageBox.critical(gui, "Invalid layout", str(e))
        return

    save_path, _ = QFileDialog.getSaveFileName(gui, "Save ISO as…", "output.iso", "ISO (*.iso)")
    if not save_path:
        return

    worker = _IsoBuildWorker(save_path, files)
    thread = QThread()
    worker.moveToThread(thread)

    # --- Callbacks ---
    def on_success(path: str):
        QMessageBox.information(gui, "Success", f"ISO created at:\n{path}")
        cleanup()

    def on_failure(msg: str):
        QMessageBox.critical(gui, "Build error", msg)
        cleanup()

    def cleanup():
        thread.quit()
        thread.wait()
        worker.deleteLater()
        thread.deleteLater()

    worker.finished.connect(on_success)
    worker.error.connect(on_failure)
    thread.started.connect(worker.run)
    thread.start()
