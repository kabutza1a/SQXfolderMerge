# SQX Folder Merge — Specification

## Overview

![Before / After diagram](multi2uniques-databanks-specV2.png)

## 1. Purpose

Collect files from multiple source folders into one target folder so that the target contains exactly one copy of each uniquely-named file.

---

## 2. Inputs

| Input | Description |
|---|---|
| Target folder path | Absolute or relative path. Created if it does not exist. |
| Source folder paths | One or more absolute or relative paths, provided in priority order. |

---

## 3. Behaviour

### 3.1 File Discovery

- The program reads the **immediate contents** of every source folder.
- Subfolders are **not** recursed into.
- Only regular files are considered; symlinks and directories inside a source folder are ignored.

### 3.2 Seen-Name Tracking

- On startup the program builds a set of filenames already present in the **target folder** (regular files only).
- This set is the "seen" set. It is updated in memory as each new file is copied.

### 3.3 Copy Rule

For each file encountered across sources (processed in source-list order, files within each source processed in alphabetical order):

```
if filename ∈ seen:
    skip (do not copy, do not overwrite)
else:
    copy file to target folder
    add filename to seen
```

### 3.4 Filename Comparison

Comparison is **case-sensitive**: `File1.sqx` and `file1.sqx` are distinct names.

> **Platform note.** macOS (HFS+) and Windows (NTFS) filesystems are case-insensitive by default. When two source files differ only by case, the OS will map both copies to the same physical target file, meaning the second copy silently overwrites the first. This is an OS-level constraint; the application logic itself is case-sensitive.

### 3.5 Priority

When the same filename exists in more than one source, the copy from the **earliest source in the provided list** is used. Later occurrences are skipped.

### 3.6 Target Pre-existing Files

Files already present in the target at run-time are treated identically to files already copied during the run — they are in the seen set from the start and will cause any matching source file to be skipped.

### 3.7 Non-destructive

- Source folders are **never modified**.
- Existing target files are **never overwritten or deleted**.

---

## 4. Outputs

### 4.1 Target Folder

After a successful run the target folder contains:

- All files that were already there before the run, unchanged.
- One copy of every additional uniquely-named file found across the source folders.

### 4.2 Log Output

Each file action is reported:

| Event | Log line |
|---|---|
| File copied | `COPY  <filename>  ← <source_folder>/` |
| File skipped | `SKIP  <filename>` |
| Source not found | `WARNING: not found, skipping: <path>` |
| Run complete | `Done.  Copied: N   Skipped: N` |

---

## 5. UI Requirements

| Element | Requirement |
|---|---|
| Source count control | Integer spin box, range 1–20. Changing the value immediately adds or removes source-row widgets. |
| Source row | One per source folder. Contains a free-text path entry and a Browse button that opens a native folder-picker dialog. |
| Target row | Free-text path entry and a Browse button. |
| Run button | Triggers the merge. Clears the log before each run. |
| Log panel | Scrollable, read-only text area. Updated line-by-line during the run. |
| Platform | Must run on macOS and Windows using Python's standard library only (tkinter). |

---

## 6. Deliverables

| File | Description |
|---|---|
| `folder_merge_ui.py` | Single-file Python application — UI and merge logic combined. |
| `folder_merge.py` | Command-line version (no UI dependency). |
| `docs/SQX-Folder-Merge_Spec.md` | This document. |
| `docs/SQX-Folder-Merge_UserGuide.md` | End-user guide. |

---

## 7. Constraints & Assumptions

- Python 3.9 or later.
- No third-party packages.
- Input validation: empty source/target paths are flagged to the user before the run starts; missing source directories produce a warning in the log but do not abort the run.
- File metadata (size, modification date, content) is **not** used in any comparison — only the filename.
- The merge is not atomic; a crash mid-run will leave the target in a partially-merged state (already-copied files remain).
