import os
import re
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from datetime import datetime
import threading
import subprocess
from PIL import Image, ImageTk

# Optional but recommended for Excel support
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class JewelryImagePuller:
    def __init__(self, root):
        self.root = root
        self.version = "1.6 (Dual-Code Search)"
        self.root.title(f"Jewelry Image Puller v{self.version}")
        self.root.geometry("1200x950")
        self.root.configure(bg="#121212")

        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        
        # Paths & Config
        self.config_dir = os.path.join(os.path.expanduser("~"), ".jewelry_image_puller")
        if not os.path.exists(self.config_dir): os.makedirs(self.config_dir)
        self.config_file = os.path.join(self.config_dir, "config_v1_6.json")

        self.colors = {
            "bg": "#121212",
            "card": "#1e1e1e",
            "accent": "#00d1b2",
            "accent_hover": "#00f2d3",
            "text": "#ffffff",
            "text_dim": "#888888",
            "success": "#00ffcc",
            "error": "#ff3860",
            "warning": "#ffdd57",
            "info": "#209cee",
            "highlight": "#a29bfe"
        }

        # Default Type mapping
        self.type_mapping = {
            'R': 'Ring',
            'E': 'Earring',
            'N': 'necklace',
            'B': 'bracelet',
            'P': 'pendant',
            'S': 'Set'
        }

        self.load_settings()
        self.create_widgets()

    def load_settings(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.source_dir.set(data.get('source', ''))
                    self.dest_dir.set(data.get('dest', ''))
                    if 'types' in data: self.type_mapping = data['types']
            except: pass

    def save_settings(self):
        data = {'source': self.source_dir.get(), 'dest': self.dest_dir.get(), 'types': self.type_mapping}
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def log(self, message, category="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.configure(state='normal')
        tag = category; prefix = "• "
        if category == "success": prefix = "✔ "
        elif category == "error": prefix = "✖ "
        elif category == "warning": prefix = "⚠ "
        elif category == "highlight": prefix = "✨ "
        
        self.log_area.insert(tk.END, f"[{timestamp}] ", "time")
        self.log_area.insert(tk.END, f"{prefix}{message}\n", tag)
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a1f", height=100)
        header.pack(fill="x")
        tk.Label(header, text="JEWELRY IMAGE PULLER", fg=self.colors["accent"], bg="#1a1a1f", font=("Segoe UI", 26, "bold")).pack(pady=(20, 0))
        tk.Label(header, text=f"PROFESSIONAL EDITION v{self.version}", fg=self.colors["text_dim"], bg="#1a1a1f", font=("Segoe UI", 10)).pack()
        
        main_container = tk.Frame(self.root, bg=self.colors["bg"], padx=30, pady=20)
        main_container.pack(expand=True, fill="both")

        # --- TOP SECTION: PATHS ---
        top_frame = tk.Frame(main_container, bg=self.colors["bg"])
        top_frame.pack(fill="x", pady=(0, 20))

        left_paths = tk.Frame(top_frame, bg=self.colors["bg"])
        left_paths.pack(side="left", fill="x", expand=True)
        self.add_path_row(left_paths, "SOURCE DRIVE (โฟลเดอร์หลักที่มี Ring, etc.)", self.source_dir)
        self.add_path_row(left_paths, "DESTINATION (ที่เก็บรูปปลายทาง)", self.dest_dir)

        right_btns = tk.Frame(top_frame, bg=self.colors["bg"])
        right_btns.pack(side="right", fill="y", padx=(20, 0))
        tk.Button(right_btns, text="📊 IMPORT EXCEL", command=self.import_excel, bg=self.colors["highlight"], fg="#121212", font=("Segoe UI", 9, "bold"), relief="flat", width=15, height=2).pack(pady=4)
        tk.Button(right_btns, text="⚙ CATEGORIES", command=self.open_category_manager, bg="#2d2d2d", fg="white", font=("Segoe UI", 9), relief="flat", width=15, height=2).pack(pady=4)

        # --- MIDDLE SECTION: IDS & LOGS ---
        mid_frame = tk.Frame(main_container, bg=self.colors["bg"])
        mid_frame.pack(fill="both", expand=True)

        # Left: ID Input
        id_frame = tk.Frame(mid_frame, bg=self.colors["bg"])
        id_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        id_hdr = tk.Frame(id_frame, bg=self.colors["bg"])
        id_hdr.pack(fill="x", pady=(0, 5))
        tk.Label(id_hdr, text="PRODUCT IDS", fg=self.colors["text_dim"], bg=self.colors["bg"], font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(id_hdr, text="CLEAR", command=lambda: self.id_input.delete("1.0", tk.END), bg="#333333", fg="white", font=("Segoe UI", 7), relief="flat", padx=8).pack(side="right")
        tk.Button(id_hdr, text="LATEST", command=self.load_last_ids, bg="#333333", fg="white", font=("Segoe UI", 7), relief="flat", padx=8).pack(side="right", padx=5)

        self.id_input = scrolledtext.ScrolledText(id_frame, bg="#000000", fg="#ffffff", font=("Consolas", 11), insertbackground="white", relief="flat", padx=10, pady=10)
        self.id_input.pack(fill="both", expand=True)
        self.setup_text_widget_enhancements(self.id_input)

        # Right: Logs
        log_frame = tk.Frame(mid_frame, bg=self.colors["bg"])
        log_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        log_hdr = tk.Frame(log_frame, bg=self.colors["bg"])
        log_hdr.pack(fill="x", pady=(0, 5))
        tk.Label(log_hdr, text="ACTIVITY LOG", fg=self.colors["text_dim"], bg=self.colors["bg"], font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(log_hdr, text="CLEAR LOGS", command=self.clear_logs, bg="#333333", fg="white", font=("Segoe UI", 7), relief="flat", padx=8).pack(side="right")

        self.log_area = scrolledtext.ScrolledText(log_frame, bg="#000000", fg="#dddddd", font=("Consolas", 9), relief="flat", padx=10, pady=10)
        self.log_area.pack(fill="both", expand=True)
        self.log_area.configure(state='disabled')
        self.log_area.tag_config("time", foreground="#444444")
        self.log_area.tag_config("success", foreground=self.colors["success"])
        self.log_area.tag_config("error", foreground=self.colors["error"])
        self.log_area.tag_config("warning", foreground=self.colors["warning"])
        self.log_area.tag_config("info", foreground=self.colors["info"])
        self.log_area.tag_config("highlight", foreground=self.colors["highlight"])

        # --- BOTTOM SECTION: ACTIONS ---
        bot_frame = tk.Frame(main_container, bg=self.colors["bg"], pady=20)
        bot_frame.pack(fill="x")

        self.pull_btn = tk.Button(bot_frame, text="🚀 START COPYING IMAGES", command=self.start_pulling, bg=self.colors["accent"], fg="#121212", font=("Segoe UI", 14, "bold"), relief="flat", height=2)
        self.pull_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        tk.Button(bot_frame, text="📂 OPEN DESTINATION", command=self.open_destination, bg="#2d2d2d", fg="white", font=("Segoe UI", 10), relief="flat", width=25, height=2).pack(side="right")

        self.progress = ttk.Progressbar(main_container, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x")

    def setup_text_widget_enhancements(self, widget):
        widget.bind("<Control-v>", lambda e: self.handle_paste(widget))
        widget.bind("<Control-V>", lambda e: self.handle_paste(widget))
        widget.bind("<Control-c>", lambda e: self.handle_copy(widget))
        widget.bind("<Control-C>", lambda e: self.handle_copy(widget))
        widget.bind("<Control-a>", lambda e: self.handle_select_all(widget))
        widget.bind("<Control-A>", lambda e: self.handle_select_all(widget))
        
        menu = tk.Menu(widget, tearoff=0, bg="#2d2d2d", fg="white", activebackground=self.colors["accent"])
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self.handle_paste(widget))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self.handle_select_all(widget))
        
        def show_menu(event): menu.tk_popup(event.x_root, event.y_root)
        widget.bind("<Button-3>", show_menu)

    def handle_paste(self, widget): widget.event_generate("<<Paste>>"); return "break"
    def handle_copy(self, widget): widget.event_generate("<<Copy>>"); return "break"
    def handle_select_all(self, widget): widget.tag_add("sel", "1.0", "end"); return "break"

    def clear_logs(self):
        self.log_area.configure(state='normal'); self.log_area.delete("1.0", tk.END); self.log_area.configure(state='disabled')

    def open_category_manager(self):
        manager = tk.Toplevel(self.root); manager.title("Categories"); manager.geometry("500x600"); manager.configure(bg="#1a1a1f"); manager.grab_set()
        tk.Label(manager, text="MANAGE CATEGORIES", fg=self.colors["accent"], bg="#1a1a1f", font=("Segoe UI", 14, "bold")).pack(pady=20)
        tree = ttk.Treeview(manager, columns=("Code", "Name"), show="headings", height=12)
        tree.heading("Code", text="Code"); tree.heading("Name", text="Folder Name"); tree.pack(padx=20, fill="both", expand=True)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for c, n in sorted(self.type_mapping.items()): tree.insert("", "end", values=(c, n))
        refresh()
        ctrl = tk.Frame(manager, bg="#1a1a1f", pady=10); ctrl.pack(fill="x", padx=20)
        c_ent = tk.Entry(ctrl, width=5, bg="#000000", fg="white"); c_ent.grid(row=0, column=0, padx=5)
        n_ent = tk.Entry(ctrl, width=15, bg="#000000", fg="white"); n_ent.grid(row=0, column=1, padx=5)
        def add():
            c, n = c_ent.get().strip().upper(), n_ent.get().strip()
            if c and n: self.type_mapping[c] = n; self.save_settings(); refresh(); c_ent.delete(0, tk.END); n_ent.delete(0, tk.END)
        tk.Button(ctrl, text="ADD", command=add, bg=self.colors["accent"]).grid(row=0, column=2)
        def delete():
            s = tree.selection()
            if s:
                code = tree.item(s[0])['values'][0]
                if messagebox.askyesno("Confirm", f"Delete '{code}'?"): del self.type_mapping[str(code)]; self.save_settings(); refresh()
        tk.Button(manager, text="DELETE SELECTED", command=delete, bg=self.colors["error"], fg="white").pack(fill="x", padx=20, pady=20)

    def import_excel(self):
        if not HAS_PANDAS:
            messagebox.showerror("Error", "Missing libraries. Please check build logs.")
            return
        
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls *.xlsm")])
        if not file_path: return

        try:
            xl = pd.ExcelFile(file_path)
            if len(xl.sheet_names) > 1:
                sheet_win = tk.Toplevel(self.root); sheet_win.title("Select Sheet"); sheet_win.geometry("300x400"); sheet_win.grab_set()
                tk.Label(sheet_win, text="CHOOSE SHEET").pack(pady=10)
                lb = tk.Listbox(sheet_win); lb.pack(fill="both", expand=True, padx=20)
                for s in xl.sheet_names: lb.insert(tk.END, s)
                def sel_sheet():
                    if not lb.curselection(): return
                    s = lb.get(lb.curselection()[0]); sheet_win.destroy(); self.show_column_picker(file_path, s)
                tk.Button(sheet_win, text="SELECT", command=sel_sheet).pack(pady=10)
            else:
                self.show_column_picker(file_path, xl.sheet_names[0])
        except Exception as e: messagebox.showerror("Error", f"Excel Error: {e}")

    def show_column_picker(self, file_path, sheet_name):
        try:
            df_full = pd.read_excel(file_path, sheet_name=sheet_name, nrows=50)
            header_row = 0; max_cols = 0
            for i in range(min(10, len(df_full))):
                cols_found = df_full.iloc[i].dropna().count()
                if cols_found > max_cols: max_cols = cols_found; header_row = i + 1
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row if header_row > 0 else 0)
            columns = [str(c) for c in df.columns if not str(c).startswith("Unnamed")]
            picker = tk.Toplevel(self.root); picker.title("Choose Column"); picker.geometry("450x550"); picker.grab_set()
            tk.Label(picker, text="SELECT COLUMN WITH PRODUCT IDS", font=("Segoe UI", 10, "bold")).pack(pady=10)
            lb = tk.Listbox(picker, font=("Consolas", 10)); lb.pack(fill="both", expand=True, padx=20)
            for c in columns: lb.insert(tk.END, c)
            def load():
                if not lb.curselection(): return
                col = lb.get(lb.curselection()[0]); picker.destroy(); self.process_excel_data(file_path, sheet_name, col, header_row)
            tk.Button(picker, text="IMPORT DATA", command=load, bg=self.colors["accent"], height=2).pack(fill="x", padx=20, pady=20)
        except Exception as e: messagebox.showerror("Error", f"Picker Error: {e}")

    def process_excel_data(self, file_path, sheet_name, column_name, header_row):
        def task():
            try:
                self.log(f"Processing Excel...", "info")
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row if header_row > 0 else 0)
                raw_ids = df[column_name].dropna().astype(str).tolist()
                valid_ids = [r.strip() for r in raw_ids if len(r.strip()) > 1]
                if not valid_ids: messagebox.showwarning("No Data", "No IDs found."); return
                cur = self.id_input.get("1.0", tk.END).strip()
                combined = (cur + "\n" + "\n".join(valid_ids)) if cur and messagebox.askyesno("Import", "Append to list?") else "\n".join(valid_ids)
                self.root.after(0, lambda: [self.id_input.delete("1.0", tk.END), self.id_input.insert("1.0", combined)])
                self.log(f"Imported {len(valid_ids)} IDs.", "success")
            except Exception as e: self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=task, daemon=True).start()

    def normalize_id(self, raw_id):
        clean = raw_id.strip().upper()
        # Legacy Code Support: TRK -> R, TEK -> E, etc.
        legacy = re.search(r'^T([REPNBS])K', clean)
        if legacy: clean = clean.replace(legacy.group(0), legacy.group(1))
        clean = re.sub(r'^([A-Z])(\d)', r'\1-\2', clean)
        clean = clean.replace(' ', '-'); clean = re.sub(r'-+', '-', clean)
        return clean

    def choose_files_visual(self, product_id, files_paths):
        if not files_paths: return []
        if len(files_paths) == 1: return files_paths
        
        # Visual Gallery Dialog - Compact & One-page feel
        win = tk.Toplevel(self.root); win.title(f"Select: {product_id}"); win.geometry("980x800"); win.configure(bg="#121212"); win.grab_set()
        res_paths = []
        header = tk.Frame(win, bg="#1a1a1f", pady=10); header.pack(fill="x")
        tk.Label(header, text=f"SELECT IMAGES FOR: {product_id}", fg=self.colors["accent"], bg="#1a1a1f", font=("Segoe UI", 12, "bold")).pack()
        
        main_scroll = tk.Frame(win, bg="#121212"); main_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        canvas = tk.Canvas(main_scroll, bg="#121212", highlightthickness=0); canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(main_scroll, orient="vertical", command=canvas.yview); scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        gallery = tk.Frame(canvas, bg="#121212"); canvas.create_window((0, 0), window=gallery, anchor="nw")

        chk_vars = []; photo_refs = []; cols = 5; r, c = 0, 0; thumb_size = (160, 160)
        for path in files_paths:
            try:
                img = Image.open(path); img.thumbnail(thumb_size); ph = ImageTk.PhotoImage(img); photo_refs.append(ph)
                f_frame = tk.Frame(gallery, bg="#1e1e1e", padx=2, pady=2, highlightthickness=1, highlightbackground="#333333"); f_frame.grid(row=r, column=c, padx=5, pady=5)
                lbl = tk.Label(f_frame, image=ph, bg="#1e1e1e", cursor="hand2"); lbl.pack()
                v = tk.BooleanVar(value=True); chk_vars.append((path, v))
                tk.Checkbutton(f_frame, text=os.path.basename(path)[:18], variable=v, bg="#1e1e1e", fg="white", selectcolor="#000", font=("Arial", 7)).pack()
                lbl.bind("<Button-1>", lambda e, var=v: var.set(not var.get()))
                c += 1
                if c >= cols: c = 0; r += 1
            except: pass
        gallery.update_idletasks(); canvas.config(scrollregion=canvas.bbox("all"))
        
        def confirm():
            for p, v in chk_vars:
                if v.get(): res_paths.append(p)
            win.destroy()
            
        btn_f = tk.Frame(win, bg="#1a1a1f", pady=15); btn_f.pack(fill="x")
        tk.Button(btn_f, text="COPY SELECTED", command=confirm, bg=self.colors["accent"], fg="#121212", font=("Segoe UI", 11, "bold"), width=25, height=2).pack(side="left", expand=True, padx=20)
        tk.Button(btn_f, text="SKIP ALL", command=win.destroy, bg="#333333", fg="white", width=15, height=2).pack(side="right", expand=True, padx=20)
        self.root.wait_window(win); return res_paths

    def start_pulling(self):
        source, dest = self.source_dir.get(), self.dest_dir.get()
        if not source or not os.path.exists(source): messagebox.showerror("Error", "Invalid Source"); return
        if not dest or not os.path.exists(dest): messagebox.showwarning("Warning", "Invalid Dest"); return
        ids_text = self.id_input.get("1.0", tk.END).strip()
        if not ids_text: messagebox.showwarning("Warning", "Enter IDs"); return
        with open(os.path.join(self.config_dir, "last_ids.txt"), 'w', encoding='utf-8') as f: f.write(ids_text)
        ids = [i.strip() for i in ids_text.split('\n') if i.strip()]
        self.pull_btn.config(state="disabled")
        threading.Thread(target=self.pull_process, args=(ids, source, dest), daemon=True).start()

    def load_last_ids(self):
        f = os.path.join(self.config_dir, "last_ids.txt")
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                self.id_input.delete("1.0", tk.END); self.id_input.insert("1.0", file.read())

    def get_range(self, num):
        start = ((num - 1) // 200) * 200 + 1
        return f"{start:03d}-{start+199:03d}"

    def find_case_insensitive(self, parent, name):
        try:
            items = os.listdir(parent)
            for i in items:
                if i.lower() == name.lower(): return os.path.join(parent, i)
            for i in items:
                if name.lower() in i.lower(): return os.path.join(parent, i)
        except: pass
        return None

    def deep_search(self, start_dir, target_id):
        matches = []
        for root, dirs, files in os.walk(start_dir):
            for f in files:
                if target_id.upper() in f.upper(): matches.append(os.path.join(root, f))
            if len(matches) > 10: break
        return matches

    def pull_process(self, ids, source, dest):
        self.progress['maximum'] = len(ids); self.progress['value'] = 0
        success, failed, missing = 0, 0, []
        self.log(f"Starting Pro Puller v1.6 (Dual-Search)...", "highlight")

        for i, raw_id in enumerate(ids):
            p_id = self.normalize_id(raw_id); potential_files = []
            try:
                # 1. Parse Normalized ID (e.g. R-10501)
                m = re.search(r'^([A-Z])-(\d+)', p_id)
                if not m:
                    self.log(f"Invalid Format: {p_id}", "error"); failed += 1; missing.append(f"{p_id} (Format)"); continue
                
                prefix, num_code = m.group(1), m.group(2)
                p_type = self.type_mapping.get(prefix, "Other")
                range_s = self.get_range(int(num_code))
                
                # Dual Search Targets: Both Modern and Legacy
                core_id = f"{prefix}-{num_code}"
                legacy_core = f"T{prefix}K-{num_code}"
                search_targets = [core_id, legacy_core]
                
                # 2. Path Finding
                t_path = self.find_case_insensitive(source, p_type)
                search_dirs = []
                if t_path:
                    r_path = self.find_case_insensitive(t_path, f"{p_type} {range_s}")
                    if not r_path: r_path = self.find_case_insensitive(t_path, range_s)
                    if r_path:
                        search_dirs.append(r_path)
                        sub = self.find_case_insensitive(r_path, "รูปสินค้า")
                        if sub: search_dirs.append(sub)

                # 3. Scanning
                for s_dir in search_dirs:
                    for item in os.listdir(s_dir):
                        item_path = os.path.join(s_dir, item)
                        if os.path.isfile(item_path):
                            item_up = item.upper()
                            if any(target in item_up for target in search_targets):
                                potential_files.append(item_path)

                # 4. Fallback: Deep Search
                if not potential_files:
                    self.log(f"Searching variants for {core_id}...", "info")
                    for target in search_targets:
                        potential_files.extend(self.deep_search(source, target))

                if not potential_files:
                    self.log(f"Not Found: {p_id}", "warning"); failed += 1; missing.append(p_id)
                else:
                    potential_files = list(set(potential_files))
                    chosen_files = self.choose_files_visual(p_id, potential_files)
                    if chosen_files:
                        for s_file in chosen_files:
                            f_n = os.path.basename(s_file); d_file = os.path.join(dest, f_n)
                            if os.path.exists(d_file):
                                b, e = os.path.splitext(f_n); d_file = os.path.join(dest, f"{b}_NEW{e}")
                            shutil.copy2(s_file, d_file); self.log(f"Copied: {os.path.basename(d_file)}", "success")
                        success += 1
                    else:
                        self.log(f"Skipped: {p_id}", "info")
            except Exception as e: self.log(f"Error {p_id}: {e}", "error"); failed += 1
            self.progress['value'] = i + 1; self.root.update_idletasks()

        if missing:
            with open(os.path.join(dest, f"missing_{datetime.now().strftime('%H%M%S')}.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(missing))
        self.log(f"Done. Found: {success}, Missing: {failed}", "highlight")
        self.pull_btn.config(state="normal")
        self.root.after(0, lambda: messagebox.showinfo("v1.6 Result", f"Finished!\nSuccess: {success}\nFailed: {failed}"))

    def add_path_row(self, parent, label, var):
        f = tk.Frame(parent, bg=self.colors["card"], padx=15, pady=8, highlightthickness=1, highlightbackground="#333333"); f.pack(fill="x", pady=4)
        tk.Label(f, text=label, fg=self.colors["text_dim"], bg=self.colors["card"], font=("Segoe UI", 8, "bold")).pack(anchor="w")
        r = tk.Frame(f, bg=self.colors["card"]); r.pack(fill="x", pady=(4, 0))
        tk.Entry(r, textvariable=var, font=("Consolas", 9), bg="#121212", fg="#ffffff", relief="flat").pack(side="left", expand=True, fill="x", ipady=5)
        tk.Button(r, text="...", command=lambda: self.browse_dir(var), bg="#333333", fg="white", width=4).pack(side="right", padx=(5, 0))

    def browse_dir(self, var):
        d = filedialog.askdirectory()
        if d: var.set(os.path.normpath(d)); self.save_settings()

    def open_destination(self):
        p = self.dest_dir.get()
        if os.path.exists(p): os.startfile(p) if hasattr(os, 'startfile') else subprocess.run(['open', p])
        else: messagebox.showwarning("Warning", "Folder not found")

if __name__ == "__main__":
    root = tk.Tk(); app = JewelryImagePuller(root); root.mainloop()
