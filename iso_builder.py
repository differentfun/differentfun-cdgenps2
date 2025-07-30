# iso_builder.py
"""Low‑level image writer for *Different Fun CDGenPS2*.

(…docstring invariata…)
"""

from __future__ import annotations
import os
from typing import BinaryIO, List, Optional, Tuple

__all__ = ["SECTOR_SIZE", "create_ps2_iso_with_lba"]

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

SECTOR_SIZE  = 2048          # bytes per sector
_CHUNK_SIZE  = 1 << 20       # 1 MiB read/write chunk

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _write_padding(fp: BinaryIO, sectors: int) -> None:
    """Write *sectors* × 2048 zero bytes to *fp*."""
    if sectors <= 0:
        return
    blank = b"\x00" * SECTOR_SIZE
    for _ in range(sectors):
        fp.write(blank)

# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def create_ps2_iso_with_lba(
    output_path: str,
    files_with_lba: List[Tuple[str, Optional[int]]],
) -> str:
    """Write a PS2‑compatible image honouring optional LBA constraints."""
    current_sector = 0

    with open(output_path, "wb") as iso:
        for file_path, target_lba in files_with_lba:
            if not os.path.exists(file_path):
                raise FileNotFoundError(file_path)

            # 1) zero‑pad up to requested LBA
            if target_lba is not None:
                if target_lba < current_sector:
                    raise ValueError(
                        f"{file_path!r} requests LBA {target_lba}, which overlaps a previous file "
                        f"ending at sector {current_sector - 1}."
                    )
                _write_padding(iso, target_lba - current_sector)
                current_sector = target_lba

            # 2) stream the file
            bytes_written = 0
            with open(file_path, "rb") as src:
                while chunk := src.read(_CHUNK_SIZE):
                    iso.write(chunk)
                    bytes_written += len(chunk)

            # 3) sector‑align (2048 B)
            if (remainder := bytes_written % SECTOR_SIZE):
                iso.write(b"\x00" * (SECTOR_SIZE - remainder))
                bytes_written += SECTOR_SIZE - remainder

            current_sector += bytes_written // SECTOR_SIZE

    return output_path
