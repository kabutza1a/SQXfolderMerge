#!/usr/bin/env python3
"""
SQX-Folder-Merge: Copy one copy of each uniquely-named file from source folders into a target folder.
Comparison is case-sensitive. Files already in target are skipped.

Usage:
    python folder_merge.py <target_folder> <source_folder1> [source_folder2 ...]
"""

import sys
import shutil
from pathlib import Path


def merge_folders(target: Path, sources: list[Path]) -> None:
    target.mkdir(parents=True, exist_ok=True)

    def visible(p: Path) -> bool:
        return p.is_file() and not p.name.startswith(".")

    pre_existing: set[str] = {f.name for f in target.iterdir() if visible(f)}
    seen: set[str] = set(pre_existing)

    if pre_existing:
        print(f"  Target already contains {len(pre_existing)} file(s) — these will not be overwritten.\n")

    seen_lower: dict[str, str] = {n.lower(): n for n in pre_existing}

    copied = 0
    skip_preexisting = 0
    skip_preexisting_names: set[str] = set()
    skip_duplicate = 0

    for source in sources:
        if not source.is_dir():
            print(f"WARNING: source folder not found, skipping: {source}")
            continue
        for src_file in sorted(source.iterdir()):
            if not visible(src_file):
                continue
            name = src_file.name
            if name in pre_existing:
                print(f"  SKIP  {name}  (already in target before run)")
                skip_preexisting += 1
                skip_preexisting_names.add(name)
            elif name in seen:
                print(f"  SKIP  {name}  (duplicate — already copied from an earlier source)")
                skip_duplicate += 1
            else:
                clash = seen_lower.get(name.lower())
                if clash:
                    print(f"  WARN  {name}  differs only by case from '{clash}' already in target"
                          f" — on case-insensitive filesystems (macOS/Windows) this will overwrite it")
                shutil.copy2(src_file, target / name)
                seen.add(name)
                seen_lower[name.lower()] = name
                print(f"  COPY  {name}  <- {source.name}/")
                copied += 1

    pre_skip_detail = (f"{skip_preexisting} skips across "
                       f"{len(skip_preexisting_names)} distinct file(s)"
                       if skip_preexisting else "0")

    print(f"\nDone.")
    print(f"  Copied:                        {copied}")
    print(f"  Skipped — pre-existing:        {pre_skip_detail}")
    print(f"  Skipped — duplicate in source: {skip_duplicate}")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python folder_merge.py <target_folder> <source_folder1> [source_folder2 ...]")
        sys.exit(1)

    target = Path(sys.argv[1])
    sources = [Path(p) for p in sys.argv[2:]]

    print(f"Target : {target}")
    print(f"Sources: {[str(s) for s in sources]}\n")

    merge_folders(target, sources)


if __name__ == "__main__":
    main()
