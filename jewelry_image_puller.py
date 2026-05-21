import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from datetime import datetime
import threading

class JewelryImagePuller:
    def __init__(self, root):
        self.root = root
        self.version = "1.2 (Pro Edition)"
        self.root.title(f"Jewelry Image Puller v{self.version}")
        self.root.geometry("1100x900")
        self.root.configure(bg="#121212")

        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        
        # Paths & Config
        self.config_dir = os.path.join(os.path.expanduser("~"), ".jewelry_image_puller")
        if not os.path.exists(self.config_dir): os.makedirs(self.config_dir)
        self.config_file = os.path.join(self.config_dir, "config_v1_2.json")

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
                    saved_mapping = data.get('types')
                    if saved_mapping:
                        self.type_mapping = saved_mapping
            except: pass

    def save_settings(self):
        data = {
            'source': self.source_dir.get(),
            'dest': self.dest_dir.get(),
            'types': self.type_mapping
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except: pass

    def log(self, message, category="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.configure(state='normal')
        tag = category
        prefix = "• "
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

        # Top Section: Paths & Settings
        top_controls = tk.Frame(main_container, bg=self.colors["bg"])
        top_controls.pack(fill="x", pady=(0, 20))

        # Paths Frame
        paths_frame = tk.Frame(top_controls, bg=self.colors["bg"])
        paths_frame.pack(side="left", fill="x", expand=True)
        self.add_path_row(paths_frame, "SOURCE DRIVE (โฟลเดอร์หลัก)", self.source_dir)
        self.add_path_row(paths_frame, "DESTINATION (ที่เก็บรูป)", self.dest_dir)

        # Settings Sidebar (Buttons)
        settings_frame = tk.Frame(top_controls, bg=self.colors["bg"])
        settings_frame.pack(side="right", fill="y", padx=(20, 0))
        tk.Button(settings_frame, text="⚙ CATEGORIES", command=self.open_category_manager, bg="#2d2d2d", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", width=15, height=2).pack(pady=5)
        tk.Button(settings_frame, text="🗑 CLEAR LOGS", command=self.clear_logs, bg="#2d2d2d", fg="white", font=("Segoe UI", 9), relief="flat", width=15, height=2).pack(pady=5)

        # Middle Section: Input and Controls
        split_frame = tk.Frame(main_container, bg=self.colors["bg"])
        split_frame.pack(fill="both", expand=True)

        # Left: ID Input
        input_frame = tk.Frame(split_frame, bg=self.colors["bg"])
        input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        input_header = tk.Frame(input_frame, bg=self.colors["bg"])
        input_header.pack(fill="x", pady=(0, 5))
        tk.Label(input_header, text="PRODUCT IDS (COPY & PASTE)", fg=self.colors["text_dim"], bg=self.colors["bg"], font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(input_header, text="LATEST IDS", command=self.load_last_ids, bg="#333333", fg="white", font=("Segoe UI", 7), relief="flat", padx=8).pack(side="right", padx=5)
        tk.Button(input_header, text="CLEAR", command=lambda: self.id_input.delete("1.0", tk.END), bg="#333333", fg="white", font=("Segoe UI", 7), relief="flat", padx=8).pack(side="right")

        self.id_input = scrolledtext.ScrolledText(input_frame, bg="#000000", fg="#ffffff", font=("Consolas", 11), insertbackground="white", relief="flat", padx=10, pady=10)
        self.id_input.pack(fill="both", expand=True)

        # Right: Logs & Actions
        control_frame = tk.Frame(split_frame, bg=self.colors["bg"])
        control_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.pull_btn = tk.Button(control_frame, text="🚀 START PULLING IMAGES", command=self.start_pulling, bg=self.colors["accent"], fg="#121212", font=("Segoe UI", 12, "bold"), relief="flat", height=2)
        self.pull_btn.pack(fill="x", pady=(0, 10))

        btn_row = tk.Frame(control_frame, bg=self.colors["bg"])
        btn_row.pack(fill="x", pady=(0, 10))
        tk.Button(btn_row, text="📂 OPEN DESTINATION", command=self.open_destination, bg="#2d2d2d", fg="white", font=("Segoe UI", 9), relief="flat", height=2).pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        tk.Label(control_frame, text="ACTIVITY LOG", fg=self.colors["text_dim"], bg=self.colors["bg"], font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 5))
        self.log_area = scrolledtext.ScrolledText(control_frame, bg="#000000", fg="#dddddd", font=("Consolas", 9), relief="flat", padx=10, pady=10)
        self.log_area.pack(fill="both", expand=True)
        self.log_area.configure(state='disabled')
        self.log_area.tag_config("time", foreground="#444444")
        self.log_area.tag_config("success", foreground=self.colors["success"])
        self.log_area.tag_config("error", foreground=self.colors["error"])
        self.log_area.tag_config("warning", foreground=self.colors["warning"])
        self.log_area.tag_config("info", foreground=self.colors["info"])
        self.log_area.tag_config("highlight", foreground=self.colors["highlight"])

        self.progress = ttk.Progressbar(main_container, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(20, 0))

    def clear_logs(self):
        self.log_area.configure(state='normal')
        self.log_area.delete("1.0", tk.END)
        self.log_area.configure(state='disabled')

    def open_category_manager(self):
        manager = tk.Toplevel(self.root)
        manager.title("Category & Type Mapping")
        manager.geometry("500x600")
        manager.configure(bg="#1a1a1f")
        manager.grab_set()

        tk.Label(manager, text="MANAGE CATEGORIES", fg=self.colors["accent"], bg="#1a1a1f", font=("Segoe UI", 14, "bold")).pack(pady=20)
        
        tree_frame = tk.Frame(manager, bg="#1a1a1f")
        tree_frame.pack(padx=20, fill="both", expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=("Code", "Name"), show="headings", height=12)
        tree.heading("Code", text="Prefix Code (e.g. R)")
        tree.heading("Name", text="Folder Name (e.g. Ring)")
        tree.column("Code", width=100, anchor="center")
        tree.pack(side="left", fill="both", expand=True)

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for c, n in sorted(self.type_mapping.items()): tree.insert("", "end", values=(c, n))
        refresh()

        input_frame = tk.Frame(manager, bg="#1a1a1f", pady=10)
        input_frame.pack(fill="x", padx=20)
        
        tk.Label(input_frame, text="CODE:", bg="#1a1a1f", fg="white").grid(row=0, column=0)
        c_ent = tk.Entry(input_frame, width=5, bg="#000000", fg="white", relief="flat")
        c_ent.grid(row=0, column=1, padx=5)
        
        tk.Label(input_frame, text="NAME:", bg="#1a1a1f", fg="white").grid(row=0, column=2)
        n_ent = tk.Entry(input_frame, width=15, bg="#000000", fg="white", relief="flat")
        n_ent.grid(row=0, column=3, padx=5)

        def add_entry():
            c, n = c_ent.get().strip().upper(), n_ent.get().strip()
            if c and n:
                self.type_mapping[c] = n
                self.save_settings()
                refresh()
                c_ent.delete(0, tk.END); n_ent.delete(0, tk.END)

        tk.Button(input_frame, text="ADD / UPDATE", command=add_entry, bg=self.colors["accent"], fg="#121212", font=("Segoe UI", 8, "bold"), relief="flat").grid(row=0, column=4, padx=5)

        def delete_entry():
            s = tree.selection()
            if s:
                code = tree.item(s[0])['values'][0]
                if messagebox.askyesno("Confirm", f"Delete mapping for '{code}'?"):
                    del self.type_mapping[str(code)]
                    self.save_settings(); refresh()

        tk.Button(manager, text="DELETE SELECTED", command=delete_entry, bg=self.colors["error"], fg="white", font=("Segoe UI", 9, "bold"), relief="flat", height=2).pack(fill="x", padx=20, pady=20)

    def load_last_ids(self):
        history_file = os.path.join(self.config_dir, "last_ids.txt")
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                self.id_input.delete("1.0", tk.END)
                self.id_input.insert("1.0", f.read())
            self.log("Loaded last used IDs.", "info")

    def save_last_ids(self, ids_text):
        history_file = os.path.join(self.config_dir, "last_ids.txt")
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write(ids_text)

    def add_path_row(self, parent, label, var):
        frame = tk.Frame(parent, bg=self.colors["card"], padx=15, pady=8, highlightthickness=1, highlightbackground="#333333")
        frame.pack(fill="x", pady=4)
        tk.Label(frame, text=label, fg=self.colors["text_dim"], bg=self.colors["card"], font=("Segoe UI", 8, "bold")).pack(anchor="w")
        row = tk.Frame(frame, bg=self.colors["card"])
        row.pack(fill="x", pady=(4, 0))
        tk.Entry(row, textvariable=var, font=("Consolas", 9), bg="#121212", fg="#ffffff", relief="flat", insertbackground="white").pack(side="left", expand=True, fill="x", ipady=5)
        tk.Button(row, text="...", command=lambda: self.browse_dir(var), bg="#333333", fg="white", relief="flat", width=4).pack(side="right", padx=(5, 0))

    def browse_dir(self, var):
        d = filedialog.askdirectory()
        if d:
            var.set(os.path.normpath(d))
            self.save_settings()

    def open_destination(self):
        path = self.dest_dir.get()
        if os.path.exists(path):
            import subprocess
            os.startfile(path) if hasattr(os, 'startfile') else subprocess.run(['open', path])
        else: messagebox.showwarning("Warning", "Destination folder does not exist.")

    def normalize_id(self, raw_id):
        """Fixes common ID errors: 'R 10250' -> 'R-10250', 'R10250' -> 'R-10250'"""
        clean = raw_id.strip().upper()
        # Add hyphen if missing between letter and number (e.g., R12345 -> R-12345)
        clean = re.sub(r'^([A-Z])(\d)', r'\1-\2', clean)
        # Replace spaces with hyphens
        clean = clean.replace(' ', '-')
        # Remove multiple hyphens
        clean = re.sub(r'-+', '-', clean)
        return clean

    def start_pulling(self):
        source = self.source_dir.get()
        dest = self.dest_dir.get()
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Source Drive path is invalid.")
            return
        if not dest or not os.path.exists(dest):
            messagebox.showwarning("Warning", "Please select a valid destination folder.")
            return
        
        ids_text = self.id_input.get("1.0", tk.END).strip()
        if not ids_text:
            messagebox.showwarning("Warning", "Please enter Product IDs.")
            return

        self.save_last_ids(ids_text)
        ids = [i.strip() for i in ids_text.split('\n') if i.strip()]
        self.pull_btn.config(state="disabled")
        threading.Thread(target=self.pull_process, args=(ids, source, dest), daemon=True).start()

    def get_range(self, num):
        start = ((num - 1) // 200) * 200 + 1
        return f"{start:03d}-{start+199:03d}"

    def find_case_insensitive(self, parent, name):
        try:
            items = os.listdir(parent)
            # Exact match first
            for item in items:
                if item.lower() == name.lower(): return os.path.join(parent, item)
            # Partial match second
            for item in items:
                if name.lower() in item.lower(): return os.path.join(parent, item)
        except: pass
        return None

    def deep_search(self, start_dir, target_id):
        """Fallback search: recursively look for ID in subfolders if range folder fails"""
        matches = []
        for root, dirs, files in os.walk(start_dir):
            for f in files:
                if target_id.upper() in f.upper():
                    matches.append(os.path.join(root, f))
            if len(matches) > 10: break # Safety limit
        return matches

    def pull_process(self, ids, source, dest):
        self.progress['maximum'] = len(ids)
        self.progress['value'] = 0
        success, failed = 0, 0
        missing_ids = []

        self.log(f"Starting Pro Puller v1.2 for {len(ids)} items...", "highlight")

        for i, raw_id in enumerate(ids):
            product_id = self.normalize_id(raw_id)
            if product_id != raw_id.upper():
                self.log(f"Normalized ID: '{raw_id}' -> '{product_id}'", "info")
            
            target_files = []
            try:
                # 1. Parse ID
                m = re.search(r'^([A-Z])-(\d+)', product_id)
                if not m:
                    self.log(f"Skipping Invalid Format: {product_id}", "error")
                    failed += 1; missing_ids.append(f"{product_id} (Invalid Format)"); continue
                
                prefix, num = m.group(1), int(m.group(2))
                p_type = self.type_mapping.get(prefix, "Other")
                range_str = self.get_range(num)
                
                # 2. Path Building
                type_path = self.find_case_insensitive(source, p_type)
                if type_path:
                    range_path = self.find_case_insensitive(type_path, f"{p_type} {range_str}")
                    if not range_path: range_path = self.find_case_insensitive(type_path, range_str)
                    
                    if range_path:
                        # Direct Search in Range Folder
                        for item in os.listdir(range_path):
                            if product_id in item.upper(): target_files.append(os.path.join(range_path, item))
                        
                        # Check Subfolder "รูปสินค้า"
                        if not target_files:
                            sub = self.find_case_insensitive(range_path, "รูปสินค้า")
                            if sub:
                                for item in os.listdir(sub):
                                    if product_id in item.upper(): target_files.append(os.path.join(sub, item))
                
                # 3. Fallback: Deep Search if still not found
                if not target_files:
                    self.log(f"Not in range folder. Trying Deep Search for {product_id}...", "warning")
                    target_files = self.deep_search(source, product_id)

                if not target_files:
                    self.log(f"Not Found: {product_id}", "warning")
                    failed += 1; missing_ids.append(product_id)
                else:
                    for src_file in target_files:
                        f_name = os.path.basename(src_file)
                        dst_file = os.path.join(dest, f_name)
                        
                        # Overwrite Protection
                        if os.path.exists(dst_file):
                            base, ext = os.path.splitext(f_name)
                            dst_file = os.path.join(dest, f"{base}_NEW{ext}")
                        
                        shutil.copy2(src_file, dst_file)
                        self.log(f"Copied: {os.path.basename(dst_file)}", "success")
                    success += 1

            except Exception as e:
                self.log(f"Error {product_id}: {e}", "error")
                failed += 1

            self.progress['value'] = i + 1
            self.root.update_idletasks()

        # Wrap up
        if missing_ids:
            rep = os.path.join(dest, f"missing_report_{datetime.now().strftime('%H%M%S')}.txt")
            with open(rep, "w", encoding="utf-8") as f:
                f.write(f"MISSING IMAGES - {datetime.now()}\n\n" + "\n".join(missing_ids))

        self.log(f"Finished. Success: {success}, Failed: {failed}", "highlight")
        self.pull_btn.config(state="normal")
        messagebox.showinfo("v1.2 Summary", f"Completed!\nFound: {success}\nMissing: {failed}\nCheck destination for report.")



if __name__ == "__main__":
    root = tk.Tk()
    app = JewelryImagePuller(root)
    root.mainloop()
