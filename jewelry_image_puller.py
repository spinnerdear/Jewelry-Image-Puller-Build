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
        self.version = "1.1 (Windows Local)"
        self.root.title(f"Jewelry Image Puller v{self.version}")
        self.root.geometry("1000x850")
        self.root.configure(bg="#121212")

        self.source_dir = tk.StringVar()
        self.dest_dir = tk.StringVar()
        
        # Load last used paths if any (simple config)
        self.config_dir = os.path.join(os.path.expanduser("~"), ".jewelry_image_puller")
        if not os.path.exists(self.config_dir): os.makedirs(self.config_dir)
        self.config_file = os.path.join(self.config_dir, "config_local.json")

        self.colors = {
            "bg": "#121212",
            "card": "#1e1e1e",
            "accent": "#00d1b2",
            "text": "#ffffff",
            "text_dim": "#888888",
            "success": "#00ffcc",
            "error": "#ff3860",
            "warning": "#ffdd57",
            "info": "#209cee"
        }

        # Type mapping based on user requirements
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
            except: pass

    def save_settings(self):
        data = {'source': self.source_dir.get(), 'dest': self.dest_dir.get()}
        try:
            import json
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
        
        self.log_area.insert(tk.END, f"[{timestamp}] ", "time")
        self.log_area.insert(tk.END, f"{prefix}{message}\n", tag)
        self.log_area.configure(state='disabled')
        self.log_area.see(tk.END)

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#1a1a1f", height=100)
        header.pack(fill="x")
        tk.Label(header, text="JEWELRY IMAGE PULLER", fg=self.colors["accent"], bg="#1a1a1f", font=("Segoe UI", 24, "bold")).pack(pady=(20, 0))
        tk.Label(header, text="LOCAL WINDOWS VERSION", fg=self.colors["text_dim"], bg="#1a1a1f", font=("Segoe UI", 9)).pack()
        
        main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=30, pady=20)
        main_frame.pack(expand=True, fill="both")

        # Top Section: Paths
        paths_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        paths_frame.pack(fill="x", pady=(0, 20))

        self.add_path_row(paths_frame, "SOURCE DRIVE (โฟลเดอร์หลักที่มี Ring, Earring, etc.)", self.source_dir)
        self.add_path_row(paths_frame, "DESTINATION FOLDER (ที่เก็บรูปปลายทาง)", self.dest_dir)

        # Middle Section: Input and Controls
        split_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        split_frame.pack(fill="both", expand=True)

        # Left: ID Input
        input_frame = tk.Frame(split_frame, bg=self.colors["bg"])
        input_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        input_header = tk.Frame(input_frame, bg=self.colors["bg"])
        input_header.pack(fill="x", pady=(0, 5))
        tk.Label(input_header, text="PRODUCT IDS (COPY & PASTE HERE)", fg=self.colors["text_dim"], bg=self.colors["bg"], font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Button(input_header, text="CLEAR ALL", command=lambda: self.id_input.delete("1.0", tk.END), bg="#333333", fg="white", font=("Segoe UI", 7), relief="flat", padx=10).pack(side="right")

        self.id_input = scrolledtext.ScrolledText(input_frame, bg="#000000", fg="#ffffff", font=("Consolas", 11), insertbackground="white", relief="flat", padx=10, pady=10)
        self.id_input.pack(fill="both", expand=True)

        # Right: Logs & Actions
        control_frame = tk.Frame(split_frame, bg=self.colors["bg"])
        control_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.pull_btn = tk.Button(control_frame, text="🚀 START COPYING", command=self.start_pulling, bg=self.colors["accent"], fg="#121212", font=("Segoe UI", 12, "bold"), relief="flat", height=2)
        self.pull_btn.pack(fill="x", pady=(0, 10))

        btn_row = tk.Frame(control_frame, bg=self.colors["bg"])
        btn_row.pack(fill="x", pady=(0, 10))
        self.open_btn = tk.Button(btn_row, text="📂 OPEN DESTINATION", command=self.open_destination, bg="#2d2d2d", fg="white", font=("Segoe UI", 9), relief="flat", height=2)
        self.open_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        tk.Label(control_frame, text="ACTIVITY LOG", fg=self.colors["text_dim"], bg=self.colors["bg"], font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(10, 5))
        self.log_area = scrolledtext.ScrolledText(control_frame, bg="#000000", fg="#dddddd", font=("Consolas", 9), relief="flat", padx=10, pady=10)
        self.log_area.pack(fill="both", expand=True)
        self.log_area.configure(state='disabled')
        self.log_area.tag_config("time", foreground="#444444")
        self.log_area.tag_config("success", foreground=self.colors["success"])
        self.log_area.tag_config("error", foreground=self.colors["error"])
        self.log_area.tag_config("warning", foreground=self.colors["warning"])
        self.log_area.tag_config("info", foreground=self.colors["info"])

        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(20, 0))

    def open_destination(self):
        path = self.dest_dir.get()
        if os.path.exists(path):
            os.startfile(path) if hasattr(os, 'startfile') else subprocess.run(['open', path])
        else:
            messagebox.showwarning("Warning", "Destination folder does not exist.")

    def add_path_row(self, parent, label, var):
        frame = tk.Frame(parent, bg=self.colors["card"], padx=15, pady=10, highlightthickness=1, highlightbackground="#333333")
        frame.pack(fill="x", pady=5)
        tk.Label(frame, text=label, fg=self.colors["text_dim"], bg=self.colors["card"], font=("Segoe UI", 8, "bold")).pack(anchor="w")
        row = tk.Frame(frame, bg=self.colors["card"])
        row.pack(fill="x", pady=(5, 0))
        tk.Entry(row, textvariable=var, font=("Consolas", 9), bg="#121212", fg="#ffffff", relief="flat", insertbackground="white").pack(side="left", expand=True, fill="x", ipady=5)
        tk.Button(row, text="...", command=lambda: self.browse_dir(var), bg="#333333", fg="white", relief="flat", width=4).pack(side="right", padx=(5, 0))

    def browse_dir(self, var):
        d = filedialog.askdirectory()
        if d:
            var.set(os.path.normpath(d))
            self.save_settings()

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
            messagebox.showwarning("Warning", "Please enter at least one Product ID.")
            return

        ids = [i.strip() for i in ids_text.split('\n') if i.strip()]
        self.pull_btn.config(state="disabled")
        threading.Thread(target=self.pull_process, args=(ids, source, dest), daemon=True).start()

    def get_range(self, num):
        start = ((num - 1) // 200) * 200 + 1
        end = start + 199
        return f"{start:03d}-{end:03d}"

    def find_case_insensitive_folder(self, parent, name):
        """Helper to find folder in case-insensitive way (good for network drives)"""
        try:
            items = os.listdir(parent)
            for item in items:
                if item.lower() == name.lower():
                    return os.path.join(parent, item)
            # Try partial match if exact fails (e.g., search for "001-200" in "Ring 001-200")
            for item in items:
                if name.lower() in item.lower():
                    return os.path.join(parent, item)
        except: pass
        return None

    def pull_process(self, ids, source, dest):
        self.progress['maximum'] = len(ids)
        self.progress['value'] = 0
        success_count = 0
        fail_count = 0
        missing_ids = []

        self.log(f"Starting process for {len(ids)} items...", "info")

        for i, product_id in enumerate(ids):
            self.log(f"Processing: {product_id}", "info")
            found_this_id = False
            try:
                # 1. Parse ID (e.g., R-10250-00-S00)
                m = re.search(r'^([A-Z])-(\d+)', product_id.upper())
                if not m:
                    self.log(f"Invalid format: {product_id}", "error")
                    fail_count += 1
                    missing_ids.append(f"{product_id} (Invalid Format)")
                    continue
                
                type_code = m.group(1)
                num = int(m.group(2))
                p_type = self.type_mapping.get(type_code, "Other")
                range_str = self.get_range(num)
                range_folder_name = f"{p_type} {range_str}"
                
                # 2. Build Search Paths
                # Structure: Source Drive > {Category} > {Category} {Range} > {ProductID}.jpg
                
                type_path = self.find_case_insensitive_folder(source, p_type)
                if not type_path:
                    self.log(f"Category folder '{p_type}' not found.", "error")
                    fail_count += 1
                    missing_ids.append(f"{product_id} (Category '{p_type}' missing)")
                    continue
                
                range_path = self.find_case_insensitive_folder(type_path, range_folder_name)
                if not range_path:
                    # Try just searching for the range string (e.g., "001-200") in the category folder
                    range_path = self.find_case_insensitive_folder(type_path, range_str)
                    
                if not range_path:
                    self.log(f"Range folder '{range_folder_name}' not found.", "error")
                    fail_count += 1
                    missing_ids.append(f"{product_id} (Range '{range_folder_name}' missing)")
                    continue

                # 3. Search for the file(s) directly in the Range folder
                try:
                    all_files = os.listdir(range_path)
                    # Support multiple formats and angles
                    target_files = [f for f in all_files if product_id.upper() in f.upper()]
                    
                    if not target_files:
                        # Try searching in a "รูปสินค้า" subfolder as a fallback
                        img_sub = self.find_case_insensitive_folder(range_path, "รูปสินค้า")
                        if img_sub:
                            all_files = os.listdir(img_sub)
                            target_files = [f for f in all_files if product_id.upper() in f.upper()]
                            range_path = img_sub # Update for copying

                    if not target_files:
                        self.log(f"File not found for {product_id}", "warning")
                        fail_count += 1
                        missing_ids.append(product_id)
                    else:
                        for f_name in target_files:
                            src_file = os.path.join(range_path, f_name)
                            dst_file = os.path.join(dest, f_name)
                            shutil.copy2(src_file, dst_file)
                            self.log(f"Copied: {f_name}", "success")
                        success_count += 1
                        found_this_id = True
                except Exception as e:
                    self.log(f"Error accessing files: {e}", "error")
                    fail_count += 1
                    missing_ids.append(f"{product_id} (Access Error: {e})")

            except Exception as e:
                self.log(f"Critical error for {product_id}: {e}", "error")
                fail_count += 1
            
            self.progress['value'] = i + 1
            self.root.update_idletasks()

        # Save missing report
        if missing_ids:
            report_path = os.path.join(dest, f"missing_images_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("--- MISSING IMAGES REPORT ---\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for mid in missing_ids:
                    f.write(f"- {mid}\n")
            self.log(f"Missing report saved to: {os.path.basename(report_path)}", "highlight")

        self.log(f"Done! Success: {success_count}, Failed: {fail_count}", "info")
        self.pull_btn.config(state="normal")
        
        result_msg = f"Process Completed.\n\nSuccessfully found: {success_count} items\nNot found/Error: {fail_count} items"
        if missing_ids:
            result_msg += f"\n\nMissing report saved to destination folder."
            
        messagebox.showinfo("Summary", result_msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = JewelryImagePuller(root)
    root.mainloop()
