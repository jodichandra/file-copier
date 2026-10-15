import os
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ==================== WinSCP Color Palette ====================
COL_BG          = "#1e1e1e"
COL_BG_ALT      = "#252526"
COL_FG_FILE     = "#d4d4d4"
COL_FG_FOLDER   = "#ffd700"
COL_FG_DRIVE    = "#7fd4ff"
COL_HEADER_BG   = "#e8e8e8"
COL_HEADER_FG   = "#000000"
COL_PATH_BG     = "#c8d0d8"
COL_PATH_FG     = "#000080"
COL_SELECT_BG   = "#3399ff"
COL_SELECT_FG   = "#ffffff"
COL_TOOLBAR_BG  = "#e8e8e8"
COL_BORDER      = "#808080"

# Log panel colors
COL_LOG_BG      = "#1e1e1e"
COL_LOG_FG_OK   = "#4ec9b0"
COL_LOG_FG_ERR  = "#f48771"
COL_LOG_FG_INFO = "#d4d4d4"
COL_LOG_FG_TIME = "#808080"

CONFIG_FILE = Path.home() / ".file_copier_config.json"


def load_config():
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[Config] Gagal baca config: {e}")
    return {}


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[Config] Gagal simpan config: {e}")


class FileCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Copier - WinSCP Style")
        self.root.geometry("1200x800")
        self.root.configure(bg=COL_TOOLBAR_BG)

        self.source_root = tk.StringVar()
        self.dest_root = tk.StringVar()
        self.current_source_dir = None
        self.current_dest_dir = None

        # Filter (pencarian)
        self.source_filter = tk.StringVar()
        self.dest_filter = tk.StringVar()
        self.source_filter.trace_add("write", lambda *a: self.refresh_source())
        self.dest_filter.trace_add("write", lambda *a: self.refresh_dest())

        self.config = load_config()

        self._setup_styles()
        self._build_ui()
        self._restore_config()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==================== ttk Styles ====================
    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("Win.TButton",
                        background=COL_TOOLBAR_BG,
                        foreground="#000000",
                        borderwidth=1,
                        relief="raised",
                        padding=(8, 3),
                        font=("Segoe UI", 9))
        style.map("Win.TButton", background=[("active", "#d0d0d0")])

        style.configure("Win.Horizontal.TProgressbar",
                        troughcolor="#c0c0c0",
                        background="#3a7bd5",
                        thickness=14)

        style.configure("Win.Treeview.Heading",
                        background=COL_HEADER_BG,
                        foreground=COL_HEADER_FG,
                        relief="raised",
                        borderwidth=1,
                        font=("Segoe UI", 9, "bold"))
        style.map("Win.Treeview.Heading", background=[("active", "#d8d8d8")])

        style.configure("Win.Treeview",
                        background=COL_BG,
                        foreground=COL_FG_FILE,
                        fieldbackground=COL_BG,
                        rowheight=22,
                        borderwidth=1,
                        relief="solid",
                        font=("Segoe UI", 9))
        style.map("Win.Treeview",
                  background=[("selected", COL_SELECT_BG)],
                  foreground=[("selected", COL_SELECT_FG)])

    # ==================== Build UI ====================
    def _build_ui(self):
        # ==== Top: Root Selection ====
        top = tk.Frame(self.root, bg=COL_TOOLBAR_BG, padx=6, pady=6)
        top.pack(fill="x")

        tk.Label(top, text="Root Sumber:", bg=COL_TOOLBAR_BG, fg="#000",
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.source_root, width=80).grid(
            row=0, column=1, padx=5, sticky="we")
        ttk.Button(top, text="📂 Pilih...", style="Win.TButton",
                   command=self.choose_source_root).grid(row=0, column=2)

        tk.Label(top, text="Root Tujuan:", bg=COL_TOOLBAR_BG, fg="#000",
                 font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Entry(top, textvariable=self.dest_root, width=80).grid(
            row=1, column=1, padx=5, pady=(4, 0), sticky="we")
        ttk.Button(top, text="📂 Pilih...", style="Win.TButton",
                   command=self.choose_dest_root).grid(row=1, column=2, pady=(4, 0))

        cfg_btn_frame = tk.Frame(top, bg=COL_TOOLBAR_BG)
        cfg_btn_frame.grid(row=0, column=3, rowspan=2, padx=(8, 0))
        ttk.Button(cfg_btn_frame, text="💾 Simpan Config", style="Win.TButton",
                   command=self.save_config_now).pack(pady=(0, 2))
        ttk.Button(cfg_btn_frame, text="🗑 Reset Config", style="Win.TButton",
                   command=self.reset_config).pack()

        top.columnconfigure(1, weight=1)

        # ==== Middle: Two Panels ====
        mid = tk.Frame(self.root, bg=COL_TOOLBAR_BG, padx=6, pady=4)
        mid.pack(fill="both", expand=True)

        self._build_panel(mid, "SUMBER", side="left")
        self._build_panel(mid, "TUJUAN", side="right")

        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)
        mid.rowconfigure(0, weight=1)

        # ==== Bottom: Progress + Status + LOG ====
        bottom = tk.Frame(self.root, bg=COL_TOOLBAR_BG, padx=6, pady=6)
        bottom.pack(fill="x")

        self.progress = ttk.Progressbar(bottom, mode="determinate",
                                        style="Win.Horizontal.TProgressbar")
        self.progress.pack(fill="x")

        self.status = tk.Label(bottom, text="Siap.", bg=COL_TOOLBAR_BG,
                               fg="#333", anchor="w", font=("Segoe UI", 9))
        self.status.pack(fill="x", pady=(4, 0))

        # ==== LOG PANEL ====
        log_outer = tk.Frame(bottom, bg=COL_TOOLBAR_BG)
        log_outer.pack(fill="x", pady=(6, 0))

        log_header = tk.Frame(log_outer, bg="#3a7bd5")
        log_header.pack(fill="x")
        tk.Label(log_header, text="📜 LOG PENGIRIMAN FILE", bg="#3a7bd5", fg="#ffffff",
                 font=("Segoe UI", 9, "bold"), anchor="w", padx=6, pady=2).pack(
            side="left", fill="x", expand=True)
        tk.Button(log_header, text="🗑 Bersihkan Log", bg="#2c5fa8", fg="#ffffff",
                  activebackground="#1f4a85", activeforeground="#ffffff",
                  relief="flat", font=("Segoe UI", 8), padx=8,
                  command=self.clear_log).pack(side="right", padx=4, pady=2)

        log_body = tk.Frame(log_outer, bg=COL_BORDER, bd=1, relief="sunken")
        log_body.pack(fill="x")

        log_vsb = ttk.Scrollbar(log_body, orient="vertical")
        log_vsb.pack(side="right", fill="y")

        self.log_text = tk.Text(log_body, height=8, bg=COL_LOG_BG, fg=COL_LOG_FG_INFO,
                                font=("Consolas", 9), wrap="none", bd=0,
                                yscrollcommand=log_vsb.set, insertbackground="#fff")
        self.log_text.pack(fill="x", expand=True)
        log_vsb.config(command=self.log_text.yview)

        # Tag warna untuk log
        self.log_text.tag_configure("time", foreground=COL_LOG_FG_TIME)
        self.log_text.tag_configure("ok", foreground=COL_LOG_FG_OK)
        self.log_text.tag_configure("err", foreground=COL_LOG_FG_ERR)
        self.log_text.tag_configure("info", foreground=COL_LOG_FG_INFO)
        self.log_text.config(state="disabled")

        # ==== Context Menus ====
        self.source_menu = tk.Menu(self.root, tearoff=0,
                                   bg="#f0f0f0", fg="#000",
                                   activebackground=COL_SELECT_BG,
                                   activeforeground="#fff",
                                   font=("Segoe UI", 9))
        self.source_menu.add_command(label="📤  Kirim ke Folder Tujuan",
                                     command=self.send_to_destination)
        self.source_menu.add_separator()
        self.source_menu.add_command(label="📂  Buka di Explorer",
                                     command=self.open_in_explorer)

        self.dest_menu = tk.Menu(self.root, tearoff=0,
                                 bg="#f0f0f0", fg="#000",
                                 activebackground=COL_SELECT_BG,
                                 activeforeground="#fff",
                                 font=("Segoe UI", 9))
        self.dest_menu.add_command(label="🗑  Hapus File/Folder",
                                   command=self.delete_from_destination)
        self.dest_menu.add_separator()
        self.dest_menu.add_command(label="📂  Buka di Explorer",
                                   command=self.open_dest_in_explorer)

    def _build_panel(self, parent, title, side):
        frame = tk.Frame(parent, bg=COL_TOOLBAR_BG, bd=1, relief="ridge")
        if side == "left":
            frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        else:
            frame.grid(row=0, column=1, sticky="nsew", padx=(3, 0))

        tk.Label(frame, text=title, bg="#3a7bd5", fg="#ffffff",
                 font=("Segoe UI", 9, "bold"), anchor="w", padx=6, pady=2
                 ).pack(fill="x")

        path_bar = tk.Frame(frame, bg=COL_PATH_BG, bd=1, relief="sunken")
        path_bar.pack(fill="x", padx=2, pady=(2, 0))

        path_lbl = tk.Label(path_bar, text="(belum dipilih)",
                            bg=COL_PATH_BG, fg=COL_PATH_FG,
                            anchor="w", font=("Consolas", 9), padx=4, pady=2)
        path_lbl.pack(fill="x")

        toolbar = tk.Frame(frame, bg=COL_TOOLBAR_BG, bd=1, relief="raised")
        toolbar.pack(fill="x", padx=2, pady=(2, 0))

        if side == "left":
            up_cmd, refresh_cmd = self.go_up_source, self.refresh_source
        else:
            up_cmd, refresh_cmd = self.go_up_dest, self.refresh_dest

        ttk.Button(toolbar, text="⬆ Up", style="Win.TButton",
                   command=up_cmd).pack(side="left", padx=2, pady=2)
        ttk.Button(toolbar, text="⟳ Refresh", style="Win.TButton",
                   command=refresh_cmd).pack(side="left", padx=2, pady=2)

        # ==== SEARCH BAR ====
        search_frame = tk.Frame(frame, bg=COL_TOOLBAR_BG, bd=1, relief="raised")
        search_frame.pack(fill="x", padx=2, pady=(2, 0))

        tk.Label(search_frame, text="🔍", bg=COL_TOOLBAR_BG, fg="#000",
                 font=("Segoe UI", 10)).pack(side="left", padx=(4, 2), pady=2)

        if side == "left":
            filter_var = self.source_filter
            clear_cmd = lambda: self.source_filter.set("")
        else:
            filter_var = self.dest_filter
            clear_cmd = lambda: self.dest_filter.set("")

        search_entry = ttk.Entry(search_frame, textvariable=filter_var,
                                 font=("Segoe UI", 9))
        search_entry.pack(side="left", fill="x", expand=True, padx=2, pady=2)

        ttk.Button(search_frame, text="✕", width=3, style="Win.TButton",
                   command=clear_cmd).pack(side="left", padx=2, pady=2)

        # ==== Treeview ====
        tree_frame = tk.Frame(frame, bg=COL_BORDER, bd=1, relief="sunken")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        columns = ("name", "size", "type", "changed")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            selectmode="extended", style="Win.Treeview",
                            yscrollcommand=vsb.set)
        vsb.config(command=tree.yview)

        tree.heading("name",    text="Name",    anchor="w")
        tree.heading("size",    text="Size",    anchor="e")
        tree.heading("type",    text="Type",    anchor="w")
        tree.heading("changed", text="Changed", anchor="w")

        tree.column("name",    width=280, anchor="w", stretch=True)
        tree.column("size",    width=80,  anchor="e", stretch=False)
        tree.column("type",    width=140, anchor="w", stretch=False)
        tree.column("changed", width=150, anchor="w", stretch=False)

        tree.tag_configure("folder",     foreground=COL_FG_FOLDER, background=COL_BG)
        tree.tag_configure("file",       foreground=COL_FG_FILE,   background=COL_BG)
        tree.tag_configure("folder_alt", foreground=COL_FG_FOLDER, background=COL_BG_ALT)
        tree.tag_configure("file_alt",   foreground=COL_FG_FILE,   background=COL_BG_ALT)
        tree.tag_configure("parent",     foreground=COL_FG_DRIVE,  background=COL_BG)

        tree.pack(fill="both", expand=True)

        if side == "left":
            self.left_list = tree
            self.left_path_label = path_lbl
            tree.bind("<Double-1>", self.on_left_double_click)
            tree.bind("<Button-3>", self.on_left_right_click)
            tree.bind("<Return>", lambda e: self.on_left_double_click(e))
        else:
            self.right_list = tree
            self.right_path_label = path_lbl
            tree.bind("<Double-1>", self.on_right_double_click)
            tree.bind("<Button-3>", self.on_right_right_click)

        return frame

    # ==================== Config ====================
    def _restore_config(self):
        src_root = self.config.get("source_root", "")
        dst_root = self.config.get("dest_root", "")
        src_cur  = self.config.get("source_current", "")
        dst_cur  = self.config.get("dest_current", "")

        if src_root and Path(src_root).exists():
            self.source_root.set(src_root)
            self.current_source_dir = Path(src_cur) if src_cur and Path(src_cur).exists() else Path(src_root)
            self.refresh_source()
            self.set_status(f"✔ Config dimuat. Root sumber: {src_root}", "#0a7d0a")
        elif src_root:
            self.set_status(f"⚠ Root sumber dari config tidak ditemukan: {src_root}", "#c00000")

        if dst_root and Path(dst_root).exists():
            self.dest_root.set(dst_root)
            self.current_dest_dir = Path(dst_cur) if dst_cur and Path(dst_cur).exists() else Path(dst_root)
            self.refresh_dest()
        elif dst_root:
            self.set_status(f"⚠ Root tujuan dari config tidak ditemukan: {dst_root}", "#c00000")

        self.log("Aplikasi dimulai.", "info")

    def _collect_config(self):
        return {
            "source_root":    self.source_root.get(),
            "dest_root":      self.dest_root.get(),
            "source_current": str(self.current_source_dir) if self.current_source_dir else "",
            "dest_current":   str(self.current_dest_dir) if self.current_dest_dir else "",
            "last_saved":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def save_config_now(self):
        cfg = self._collect_config()
        save_config(cfg)
        self.config = cfg
        self.set_status(f"✔ Config disimpan ke: {CONFIG_FILE}", "#0a7d0a")
        messagebox.showinfo("Config Tersimpan",
                            f"Konfigurasi berhasil disimpan.\n\n{CONFIG_FILE}")

    def reset_config(self):
        if not messagebox.askyesno("Reset Config",
                                   "Hapus konfigurasi tersimpan?\n\n"
                                   "Aplikasi akan mulai kosong saat dibuka lagi."):
            return
        try:
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
            self.config = {}
            self.set_status("✔ Config dihapus.", "#0a7d0a")
            messagebox.showinfo("Reset", "Config berhasil dihapus.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal hapus config:\n{e}")

    def _on_close(self):
        try:
            save_config(self._collect_config())
        except Exception as e:
            print(f"[Config] Gagal auto-save: {e}")
        self.root.destroy()

    # ==================== Root Selection ====================
    def choose_source_root(self):
        initial = self.source_root.get() or str(Path.home())
        path = filedialog.askdirectory(title="Pilih Root Folder Sumber",
                                       initialdir=initial if Path(initial).exists() else None)
        if not path:
            return
        self.source_root.set(path)
        self.current_source_dir = Path(path)
        self.source_filter.set("")
        self.refresh_source()
        self.config = self._collect_config()
        save_config(self.config)

    def choose_dest_root(self):
        initial = self.dest_root.get() or str(Path.home())
        path = filedialog.askdirectory(title="Pilih Root Folder Tujuan",
                                       initialdir=initial if Path(initial).exists() else None)
        if not path:
            return
        self.dest_root.set(path)
        self.current_dest_dir = Path(path)
        self.dest_filter.set("")
        self.refresh_dest()
        self.config = self._collect_config()
        save_config(self.config)

    # ==================== Listing ====================
    def _populate(self, tree, directory: Path, filter_text: str = "", show_parent=True):
        tree.delete(*tree.get_children())
        try:
            entries = list(directory.iterdir())
        except PermissionError:
            self.set_status(f"Akses ditolak: {directory}", "red")
            return
        except FileNotFoundError:
            return

        entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

        # Filter pencarian
        ft = filter_text.strip().lower()
        if ft:
            entries = [e for e in entries if ft in e.name.lower()]

        if show_parent and directory.parent != directory and not ft:
            tree.insert("", "end",
                        values=("📁 ..", "", "Parent directory", ""),
                        tags=("parent", str(directory.parent), "dir"))

        idx = 0
        for entry in entries:
            try:
                is_dir = entry.is_dir()
                try:
                    mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                    changed = mtime.strftime("%d/%m/%Y %H:%M:%S")
                except Exception:
                    changed = ""

                if is_dir:
                    icon = "📁"
                    size_str = ""
                    type_str = "File folder"
                    tag = "folder" if idx % 2 == 0 else "folder_alt"
                else:
                    icon = "📄"
                    try:
                        size_str = self._fmt_size(entry.stat().st_size)
                    except Exception:
                        size_str = ""
                    type_str = self._file_type(entry.suffix)
                    tag = "file" if idx % 2 == 0 else "file_alt"

                tree.insert("", "end",
                            values=(f"{icon} {entry.name}", size_str, type_str, changed),
                            tags=(tag, str(entry), "dir" if is_dir else "file"))
                idx += 1
            except Exception:
                continue

    @staticmethod
    def _fmt_size(size):
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def _file_type(ext):
        ext = ext.lower()
        mapping = {
            ".php": "PHP Source File", ".html": "HTML Document",
            ".htm": "HTML Document", ".css": "Cascading Style Sheet",
            ".js": "JavaScript File", ".json": "JSON File",
            ".xml": "XML Document", ".txt": "Text Document",
            ".md": "Markdown File", ".py": "Python Source File",
            ".sql": "SQL File", ".ini": "Configuration File",
            ".log": "Log File", ".zip": "ZIP Archive",
            ".rar": "RAR Archive", ".7z": "7-Zip Archive",
            ".png": "PNG Image", ".jpg": "JPEG Image",
            ".jpeg": "JPEG Image", ".gif": "GIF Image",
            ".svg": "SVG Image", ".ico": "Icon File",
            ".pdf": "PDF Document", ".doc": "Word Document",
            ".docx": "Word Document", ".xls": "Excel Worksheet",
            ".xlsx": "Excel Worksheet", ".exe": "Application",
            ".dll": "Application Extension",
        }
        return mapping.get(ext, ext.replace(".", "").upper() + " File" if ext else "File")

    def refresh_source(self):
        if self.current_source_dir and self.current_source_dir.exists():
            self._populate(self.left_list, self.current_source_dir,
                           filter_text=self.source_filter.get())
            self.left_path_label.config(text=str(self.current_source_dir))
        else:
            self.left_path_label.config(text="(belum dipilih)")

    def refresh_dest(self):
        if self.current_dest_dir and self.current_dest_dir.exists():
            self._populate(self.right_list, self.current_dest_dir,
                           filter_text=self.dest_filter.get())
            self.right_path_label.config(text=str(self.current_dest_dir))
        else:
            self.right_path_label.config(text="(belum dipilih)")

    # ==================== Navigation ====================
    def go_up_source(self):
        if self.current_source_dir and self.current_source_dir.parent != self.current_source_dir:
            self.current_source_dir = self.current_source_dir.parent
            self.source_filter.set("")
            self.refresh_source()
            save_config(self._collect_config())

    def go_up_dest(self):
        if self.current_dest_dir and self.current_dest_dir.parent != self.current_dest_dir:
            self.current_dest_dir = self.current_dest_dir.parent
            self.dest_filter.set("")
            self.refresh_dest()
            save_config(self._collect_config())

    def on_left_double_click(self, event=None):
        sel = self.left_list.selection()
        if not sel:
            return
        item = self.left_list.item(sel[0])
        tags = item["tags"]
        path = Path(tags[1])
        if path.is_dir():
            self.current_source_dir = path
            self.source_filter.set("")
            self.refresh_source()
            save_config(self._collect_config())

    def on_right_double_click(self, event=None):
        sel = self.right_list.selection()
        if not sel:
            return
        item = self.right_list.item(sel[0])
        tags = item["tags"]
        path = Path(tags[1])
        if path.is_dir():
            self.current_dest_dir = path
            self.dest_filter.set("")
            self.refresh_dest()
            save_config(self._collect_config())

    # ==================== Right Click Handlers ====================
    def on_left_right_click(self, event):
        row = self.left_list.identify_row(event.y)
        if row:
            if row not in self.left_list.selection():
                self.left_list.selection_set(row)
            tags = self.left_list.item(row)["tags"]
            if "parent" in tags:
                return
            self.source_menu.tk_popup(event.x_root, event.y_root)

    def on_right_right_click(self, event):
        row = self.right_list.identify_row(event.y)
        if row:
            if row not in self.right_list.selection():
                self.right_list.selection_set(row)
            tags = self.right_list.item(row)["tags"]
            if "parent" in tags:
                return
            self.dest_menu.tk_popup(event.x_root, event.y_root)

    # ==================== Source Actions ====================
    def open_in_explorer(self):
        sel = self.left_list.selection()
        if not sel:
            return
        tags = self.left_list.item(sel[0])["tags"]
        path = Path(tags[1])
        folder = path if path.is_dir() else path.parent
        try:
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ==================== Destination Actions ====================
    def open_dest_in_explorer(self):
        sel = self.right_list.selection()
        if not sel:
            return
        tags = self.right_list.item(sel[0])["tags"]
        path = Path(tags[1])
        folder = path if path.is_dir() else path.parent
        try:
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_from_destination(self):
        """Hapus file/folder dari panel TUJUAN."""
        sel = self.right_list.selection()
        if not sel:
            return

        items = []
        for i in sel:
            tags = self.right_list.item(i)["tags"]
            if "parent" in tags:
                continue
            items.append(Path(tags[1]))

        if not items:
            return

        # Validasi keamanan: tidak boleh hapus di luar root tujuan
        dest_root = Path(self.dest_root.get()) if self.dest_root.get() else None
        if dest_root:
            for it in items:
                try:
                    it.resolve().relative_to(dest_root.resolve())
                except ValueError:
                    messagebox.showerror("Ditolak",
                                         f"Tidak boleh menghapus di luar root tujuan:\n{it}")
                    return

        # Konfirmasi
        preview = "\n".join(f"  • {p.name}" + ("  [FOLDER]" if p.is_dir() else "") for p in items[:10])
        if len(items) > 10:
            preview += f"\n  ... dan {len(items) - 10} item lainnya."

        if not messagebox.askyesno(
                "Konfirmasi Hapus",
                f"Hapus {len(items)} item dari folder TUJUAN?\n\n"
                f"Lokasi: {self.current_dest_dir}\n\n"
                f"{preview}\n\n"
                f"⚠ File yang dihapus TIDAK bisa dikembalikan!\n"
                f"(Tidak masuk Recycle Bin)"):
            return

        deleted_ok = 0
        errors = []
        for path in items:
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                deleted_ok += 1
                self.log(f"🗑  DEL: {path}", "err")
            except Exception as e:
                errors.append(f"{path} -> {e}")
                self.log(f"✘ Gagal hapus: {path} ({e})", "err")

        self.refresh_dest()
        if errors:
            messagebox.showwarning("Selesai dengan error",
                                   f"Berhasil hapus {deleted_ok}/{len(items)} item.\n\n"
                                   f"Error:\n" + "\n".join(errors[:10]))
        else:
            self.set_status(f"✔ {deleted_ok} item berhasil dihapus dari tujuan.", "#0a7d0a")

    # ==================== Copy ====================
    def send_to_destination(self):
        if not self.dest_root.get():
            messagebox.showwarning("Peringatan", "Root folder tujuan belum dipilih!")
            return
        if not self.source_root.get():
            messagebox.showwarning("Peringatan", "Root folder sumber belum dipilih!")
            return

        sel = self.left_list.selection()
        if not sel:
            return

        items = []
        for i in sel:
            tags = self.left_list.item(i)["tags"]
            if "parent" in tags:
                continue
            items.append(Path(tags[1]))

        if not items:
            return

        source_root = Path(self.source_root.get())
        dest_root = Path(self.dest_root.get())

        has_dir = any(p.is_dir() for p in items)
        msg = f"Kirim {len(items)} item ke:\n{dest_root}"
        if has_dir:
            msg += "\n\n(Peringatan: folder akan di-copy secara rekursif)"
        if not messagebox.askyesno("Konfirmasi", msg):
            return

        # LOG HEADER PENGIRIMAN
        self.log("=" * 80, "info")
        self.log(f"📤 KIRIM FILE — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")
        self.log(f"   Dari  : {source_root}", "info")
        self.log(f"   Ke    : {dest_root}", "info")
        self.log(f"   Jumlah: {len(items)} item", "info")
        self.log("-" * 80, "info")

        threading.Thread(
            target=self._do_copy,
            args=(items, source_root, dest_root),
            daemon=True
        ).start()

    def _do_copy(self, items, source_root, dest_root):
        all_files = []
        for item in items:
            if item.is_dir():
                for f in item.rglob("*"):
                    if f.is_file():
                        all_files.append(f)
            else:
                all_files.append(item)

        total = len(all_files)
        self.progress["maximum"] = max(total, 1)
        self.progress["value"] = 0

        copied = 0
        errors = []

        for idx, src_file in enumerate(all_files, start=1):
            try:
                try:
                    rel = src_file.relative_to(source_root)
                except ValueError:
                    rel = Path(src_file.name)

                dest_file = dest_root / rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
                copied += 1

                # Log tiap file: dari folder mana → ke folder mana
                src_folder = src_file.parent
                dst_folder = dest_file.parent
                self.root.after(0, lambda a=src_folder, b=dst_folder, n=src_file.name:
                                self.log(f"✔ [{idx}/{total}] {n}\n     FROM: {a}\n     TO  : {b}", "ok"))

                self.root.after(0, lambda v=idx: self.progress.configure(value=v))
                self.root.after(0, lambda s=rel: self.set_status(f"✔ {s}", "#0a7d0a"))
            except Exception as e:
                errors.append(f"{src_file} -> {e}")
                self.root.after(0, lambda s=src_file, err=e:
                                self.log(f"✘ GAGAL: {s}\n     ERROR: {err}", "err"))
                self.root.after(0, lambda s=src_file: self.set_status(f"✘ Gagal: {s}", "#c00000"))

        def finish():
            self.progress["value"] = total
            self.refresh_dest()
            self.log("-" * 80, "info")
            if errors:
                self.log(f"⚠ SELESAI dengan error: {copied}/{total} file berhasil.", "err")
                summary = f"Selesai: {copied}/{total} file.\n\nError:\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    summary += f"\n... dan {len(errors) - 10} error lainnya."
                messagebox.showwarning("Selesai dengan error", summary)
            else:
                self.log(f"✔ SELESAI: {copied} file berhasil dicopy.", "ok")
                messagebox.showinfo("Selesai", f"Berhasil meng-copy {copied} file ke:\n{dest_root}")
            self.set_status(f"Selesai. {copied} file berhasil dicopy.", "#0a7d0a")

        self.root.after(0, finish)

    # ==================== Log ====================
    def log(self, message: str, tag: str = "info"):
        """Tambah baris ke panel log (dengan timestamp)."""
        ts = datetime.now().strftime("[%H:%M:%S] ")
        self.log_text.config(state="normal")
        self.log_text.insert("end", ts, "time")
        self.log_text.insert("end", message + "\n", tag)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    # ==================== Helpers ====================
    def set_status(self, text, color="#333"):
        self.status.config(text=text, fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopierApp(root)
    root.mainloop()