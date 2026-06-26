# SQX Folder Merge — User Guide

## What It Does

SQX Folder Merge copies files from one or more **source folders** into a single **target folder**, ensuring each filename appears only once. If a file with the same name already exists in the target it is left untouched and the incoming file is skipped. Filename comparison is **case-sensitive** (`File1.sqx` and `file1.sqx` are treated as different names).

---

## Requirements

- Python 3.9 or later
- No third-party packages required (uses Python's standard library only)
- Works on macOS and Windows

---

## Starting the App

```
python3 folder_merge_ui.py
```

On Windows you can double-click `folder_merge_ui.py` if Python is associated with `.py` files, or run:

```
python folder_merge_ui.py
```

---

## The Interface

```
┌─────────────────────────────────────────────────────────────┐
│  Number of source folders:  [ 2 ▲▼ ]                        │
│                                                             │
│ ┌─ Source Folders ─────────────────────────────────────────┐│
│ │ Source 1: [/path/to/folderA          ] [ Browse… ]       ││
│ │ Source 2: [/path/to/folderB          ] [ Browse… ]       ││
│ └──────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─ Target Folder ──────────────────────────────────────────┐│
│ │ [/path/to/target                     ] [ Browse… ]       ││
│ └──────────────────────────────────────────────────────────┘│
│                                                             │
│                   [ Run Merge ]                             │
│                                                             │
│ ┌─ Log ────────────────────────────────────────────────────┐│
│ │  COPY  File1.sqx  ← folderA/                             ││
│ │  COPY  file2.sqa  ← folderA/                             ││
│ │  SKIP  file2.sqa  (already in target)                    ││
│ │  Done.  Copied: 5   Skipped: 2                           ││
│ └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Number of source folders

Use the spin control to set how many source folders you need (1–20). The source rows below update immediately. You can also type a number directly into the box and press **Return**.

### Source Folders

For each source row you can either:

- Type or paste a full folder path directly into the text box, or
- Click **Browse…** to open a folder-picker dialog.

Sources are processed in the order they appear (Source 1 first, Source 2 second, and so on). This matters when the same filename exists in more than one source: the **first occurrence wins** and later duplicates are skipped.

### Target Folder

The folder where all unique files will be collected. It does not need to exist — the app will create it. Any files already present in the target are counted as "already seen" and will cause matching source files to be skipped.

Type a path or click **Browse…**.

### Run Merge

Starts the operation. The **Log** panel shows every file processed:

| Message | Meaning |
|---|---|
| `COPY  filename  ← source/` | File copied into target |
| `SKIP  filename` | Filename already exists in target; file not copied |
| `WARNING: not found, skipping: …` | A source path could not be found |
| `Done.  Copied: N   Skipped: N` | Summary line at the end |

The log is cleared each time you press **Run Merge**.

---

## Example

![Before / After diagram](multi2uniques-databanks-specV2.png)

**Before:**

| Source A | Source B | Source C | Target D |
|---|---|---|---|
| File1.sqx | File1.md | File1.md | xx.sqx |
| file2.sqa | file1.sqx | file4.sqa | |
| file 3.txt | file2.sqa | file 3.txt | |
| | file 3.txt | | |

**After running** with sources A, B, C and target D:

| Target D |
|---|
| xx.sqx *(was already there)* |
| File1.sqx *(from A)* |
| file2.sqa *(from A)* |
| file 3.txt *(from A)* |
| File1.md *(from B — first occurrence)* |
| file1.sqx *(from B — different case from File1.sqx)* |
| file4.sqa *(from C)* |

Files skipped: `File1.md` from C (already copied from B), `file2.sqa` from B and C, `file 3.txt` from B and C.

---

## Notes

- **Subfolders are not scanned.** Only the immediate files inside each source folder are considered; nested subfolders are ignored.
- **Files are not moved.** Source folders are never modified; files are only read and copied.
- **Existing target files are never overwritten.** If a filename is already in the target it is always skipped, regardless of file size, date, or content.
- **Case sensitivity on macOS/Windows.** Both operating systems use case-insensitive filesystems by default, so even though the app treats `File1.sqx` and `file1.sqx` as distinct names, the OS may map both to the same physical file. On Linux (ext4, etc.) case sensitivity is fully honoured.
