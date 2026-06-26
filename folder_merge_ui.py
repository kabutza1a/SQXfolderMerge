#!/usr/bin/env python3
"""
SQX-Folder-Merge UI
"""

import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext


# ── core merge logic ──────────────────────────────────────────────────────────

def merge_folders(target: Path, sources: list[Path], log) -> None:
    target.mkdir(parents=True, exist_ok=True)

    def visible(p: Path) -> bool:
        return p.is_file() and not p.name.startswith(".")

    # Snapshot what is already in the target before we touch anything
    pre_existing: set[str] = {f.name for f in target.iterdir() if visible(f)}
    seen: set[str] = set(pre_existing)

    if pre_existing:
        log(f"  Target already contains {len(pre_existing)} file(s) — these will not be overwritten.\n")

    copied = 0
    skip_preexisting = 0   # was in target before this run
    skip_duplicate = 0     # first seen in an earlier source during this run

    for source in sources:
        if not source.is_dir():
            log(f"WARNING: not found, skipping: {source}")
            continue
        for src_file in sorted(source.iterdir()):
            if not visible(src_file):
                continue
            name = src_file.name
            if name in pre_existing:
                log(f"  SKIP  {name}  (already in target before run)")
                skip_preexisting += 1
            elif name in seen:
                log(f"  SKIP  {name}  (duplicate — already copied from an earlier source)")
                skip_duplicate += 1
            else:
                shutil.copy2(src_file, target / name)
                seen.add(name)
                log(f"  COPY  {name}  ← {source.name}/")
                copied += 1

    log(f"\nDone.")
    log(f"  Copied:                        {copied}")
    log(f"  Skipped — pre-existing:        {skip_preexisting}")
    log(f"  Skipped — duplicate in source: {skip_duplicate}")


# ── UI ────────────────────────────────────────────────────────────────────────

SHERWOOD   = "#2E5B2E"   # Sherwood green — buttons
BG         = "#6D8C6D"   # Sherwood green @ 70% over white — window / frames
BG_LABEL   = "#6D8C6D"   # same for label frames
FG         = "#FFFFFF"   # white text on green surfaces
BTN_ACTIVE = "#245224"   # slightly darker for hover/press


def _browse_btn(parent, text, command):
    """Consistent Browse button style."""
    return tk.Button(parent, text=text, command=command,
                     bg=SHERWOOD, fg="#111111", activebackground=BTN_ACTIVE,
                     activeforeground="#111111", relief="flat",
                     highlightthickness=0, overrelief="flat",
                     font=("", 11, "bold"), padx=10, pady=4)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SQX Folder Merge")
        self.resizable(True, True)
        self.minsize(600, 400)
        self.configure(bg=BG)

        self._source_rows: list[tuple[tk.StringVar, tk.Entry]] = []

        self._build_ui()
        self._set_source_count(2)

    def _build_ui(self):
        pad = dict(padx=8, pady=4)

        # ── source count ──
        count_frame = tk.Frame(self, bg=BG)
        count_frame.pack(fill="x", **pad)
        tk.Label(count_frame, text="Number of source folders:",
                 bg=BG, fg=FG).pack(side="left")
        self._count_var = tk.StringVar(value="2")
        count_spin = tk.Spinbox(count_frame, from_=1, to=20, width=4,
                                textvariable=self._count_var, command=self._on_count)
        count_spin.pack(side="left", padx=4)
        count_spin.bind("<Return>", lambda _: self._on_count())
        count_spin.bind("<FocusOut>", lambda _: self._on_count())

        # ── source rows container ──
        self._sources_frame = tk.LabelFrame(self, text="Source Folders",
                                            bg=BG_LABEL, fg=FG)
        self._sources_frame.pack(fill="x", **pad)

        # ── target folder ──
        target_frame = tk.LabelFrame(self, text="Target Folder",
                                     bg=BG_LABEL, fg=FG)
        target_frame.pack(fill="x", **pad)
        self._target_var = tk.StringVar()
        tk.Entry(target_frame, textvariable=self._target_var, width=60).pack(
            side="left", fill="x", expand=True, padx=4, pady=4)
        _browse_btn(target_frame, "Browse…", self._browse_target).pack(
            side="left", padx=4, pady=4)

        # ── run button ──
        tk.Button(self, text="Run Merge",
                  bg=SHERWOOD, fg="#111111", activebackground=BTN_ACTIVE,
                  activeforeground="#111111", relief="flat",
                  highlightthickness=0, overrelief="flat",
                  font=("", 14, "bold"), padx=20, pady=8,
                  command=self._run).pack(pady=10)

        # ── log ──
        log_frame = tk.LabelFrame(self, text="Log", bg=BG_LABEL, fg=FG)
        log_frame.pack(fill="both", expand=True, **pad)
        self._log = scrolledtext.ScrolledText(log_frame, height=10, state="disabled",
                                              font=("Courier", 10))
        self._log.pack(fill="both", expand=True, padx=4, pady=4)

    # ── source row management ─────────────────────────────────────────────────

    def _make_source_row(self, index: int) -> tuple[tk.StringVar, tk.Entry]:
        row = tk.Frame(self._sources_frame, bg=BG_LABEL)
        row.pack(fill="x", padx=4, pady=2)
        tk.Label(row, text=f"Source {index + 1}:", width=9, anchor="w",
                 bg=BG_LABEL, fg=FG).pack(side="left")
        var = tk.StringVar()
        entry = tk.Entry(row, textvariable=var, width=55)
        entry.pack(side="left", fill="x", expand=True, padx=4)
        _browse_btn(row, "Browse…",
                    lambda v=var: self._browse_source(v)).pack(side="left")
        return var, entry

    def _set_source_count(self, n: int):
        # destroy excess rows
        for widget in self._sources_frame.winfo_children():
            widget.destroy()
        self._source_rows.clear()
        for i in range(n):
            self._source_rows.append(self._make_source_row(i))

    def _on_count(self):
        try:
            n = int(self._count_var.get())
        except ValueError:
            return
        n = max(1, min(n, 20))
        self._set_source_count(n)

    # ── browse helpers ────────────────────────────────────────────────────────

    def _initial_dir(self, var: tk.StringVar) -> Path:
        """Start the folder picker at the path already typed, or cwd."""
        p = Path(var.get().strip())
        if p.is_dir():
            return p
        if p.parent.is_dir():
            return p.parent
        return Path.cwd()

    def _browse_source(self, var: tk.StringVar):
        path = filedialog.askdirectory(title="Select source folder",
                                       initialdir=self._initial_dir(var))
        if path:
            var.set(path)

    def _browse_target(self):
        path = filedialog.askdirectory(title="Select target folder",
                                       initialdir=self._initial_dir(self._target_var))
        if path:
            self._target_var.set(path)

    # ── run ───────────────────────────────────────────────────────────────────

    def _log_line(self, text: str):
        self._log.configure(state="normal")
        self._log.insert("end", text + "\n")
        self._log.see("end")
        self._log.configure(state="disabled")

    def _run(self):
        target_str = self._target_var.get().strip()
        if not target_str:
            messagebox.showerror("Missing target", "Please set a target folder.")
            return
        sources = [Path(v.get().strip()) for v, _ in self._source_rows if v.get().strip()]
        if not sources:
            messagebox.showerror("Missing sources", "Please set at least one source folder.")
            return

        self._log.configure(state="normal")
        self._log.delete("1.0", "end")
        self._log.configure(state="disabled")

        self._log_line(f"Target : {target_str}")
        for s in sources:
            self._log_line(f"Source : {s}")
        self._log_line("")

        try:
            merge_folders(Path(target_str), sources, self._log_line)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    App().mainloop()
