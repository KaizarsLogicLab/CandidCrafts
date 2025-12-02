import customtkinter as ctk
import json
import os
import shutil
import time
from tkinter import filedialog, messagebox

# --- CONFIGURATION ---
JSON_FILE = 'products.json'
IMAGE_DIR = 'assets/img/products'
PORTFOLIO_DIR = 'assets/img/portfolio'  # New folder for portfolio images
THEME_COLOR = "#D48C9E"  # Candid Craft Pink

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ProductEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Candid Craft | Store Manager (Offline)")
        self.geometry("1100x700")
        
        # Ensure directories exist
        for d in [IMAGE_DIR, PORTFOLIO_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
        
        # Data placeholder
        self.data = {}
        self.current_selection_id = None # Can be category_id or 'portfolio'
        self.mode = 'store' # 'store' or 'portfolio'
        
        # Layout Config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Candid Craft\nManager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Category List
        self.cat_scroll = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Shop Categories")
        self.cat_scroll.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(1, weight=1)

        # Sidebar Buttons
        self.add_cat_btn = ctk.CTkButton(self.sidebar_frame, text="+ New Category", fg_color="transparent", border_width=1, command=self.add_category_popup)
        self.add_cat_btn.grid(row=2, column=0, padx=20, pady=(10, 5))
        
        # Portfolio Toggle
        self.portfolio_btn = ctk.CTkButton(self.sidebar_frame, text="🎨 Manage Portfolio", fg_color=THEME_COLOR, command=self.switch_to_portfolio)
        self.portfolio_btn.grid(row=3, column=0, padx=20, pady=20)

        # --- MAIN AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.header_label = ctk.CTkLabel(self.header_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(side="left")

        self.add_item_btn = ctk.CTkButton(self.header_frame, text="+ Add Item", state="disabled", fg_color=THEME_COLOR, command=self.add_item_popup)
        self.add_item_btn.pack(side="right")

        # List Area
        self.list_scroll = ctk.CTkScrollableFrame(self.main_frame)
        self.list_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Load Data
        self.load_json()

    # --- JSON HANDLING ---
    def load_json(self):
        if not os.path.exists(JSON_FILE):
            default_data = {
                "settings": {"storeName": "Candid Craft", "currency": "₹", "whatsappPhone": "919876543210"},
                "categories": [],
                "portfolio": []
            }
            with open(JSON_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
        
        try:
            with open(JSON_FILE, 'r') as f:
                self.data = json.load(f)
            
            # Ensure portfolio key exists for older versions
            if "portfolio" not in self.data:
                self.data["portfolio"] = []
                
            self.refresh_sidebar()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON: {e}")

    def save_json(self):
        try:
            with open(JSON_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
            print("Auto-saved changes.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON: {e}")

    # --- NAVIGATION LOGIC ---
    def refresh_sidebar(self):
        for widget in self.cat_scroll.winfo_children():
            widget.destroy()
        
        for cat in self.data.get("categories", []):
            btn = ctk.CTkButton(
                self.cat_scroll, 
                text=cat['name'], 
                fg_color="transparent", 
                border_width=1, 
                text_color=("gray10", "gray90"),
                command=lambda c=cat: self.select_category(c)
            )
            btn.pack(fill="x", pady=2)

    def select_category(self, category):
        self.mode = 'store'
        self.current_selection_id = category['id']
        self.header_label.configure(text=f"📂 {category['name']}")
        self.add_item_btn.configure(text="+ Add Product", state="normal")
        self.refresh_list()

    def switch_to_portfolio(self):
        self.mode = 'portfolio'
        self.current_selection_id = 'portfolio'
        self.header_label.configure(text="🎨 Portfolio Gallery")
        self.add_item_btn.configure(text="+ Add Image", state="normal")
        self.refresh_list()

    def add_category_popup(self):
        dialog = ctk.CTkInputDialog(text="Enter Category Name:", title="New Category")
        name = dialog.get_input()
        if name:
            cat_id = name.lower().replace(" ", "-")
            new_cat = { "id": cat_id, "name": name, "icon": "fa-box", "products": [] }
            self.data['categories'].append(new_cat)
            self.save_json()
            self.refresh_sidebar()

    # --- LIST RENDERING ---
    def refresh_list(self):
        for widget in self.list_scroll.winfo_children():
            widget.destroy()

        items = []
        if self.mode == 'store':
            cat = next((c for c in self.data['categories'] if c['id'] == self.current_selection_id), None)
            if cat: items = cat['products']
        else:
            items = self.data['portfolio']

        for index, item in enumerate(items):
            self.create_item_card(item, index)

    def create_item_card(self, item, index):
        card = ctk.CTkFrame(self.list_scroll, fg_color=("gray90", "gray20"))
        card.pack(fill="x", pady=5, padx=5)

        # Icon/Image Indicator
        ctk.CTkLabel(card, text="🖼️", font=("Arial", 20)).pack(side="left", padx=10)

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        title = item.get('name') if self.mode == 'store' else item.get('title', 'Untitled')
        subtitle = f"₹{item.get('price')}" if self.mode == 'store' else item.get('image', 'No image')
        
        ctk.CTkLabel(info_frame, text=title, font=("Arial", 16, "bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=subtitle, text_color="gray").pack(anchor="w")

        # Actions
        ctk.CTkButton(card, text="Delete", width=60, fg_color="#D9534F", command=lambda: self.delete_item(index)).pack(side="right", padx=5)
        ctk.CTkButton(card, text="Edit", width=60, fg_color="#5BC0DE", command=lambda: self.edit_item_popup(item, index)).pack(side="right", padx=5)

    # --- CRUD OPERATIONS ---
    def delete_item(self, index):
        if messagebox.askyesno("Confirm", "Delete this item?"):
            if self.mode == 'store':
                cat = next((c for c in self.data['categories'] if c['id'] == self.current_selection_id), None)
                cat['products'].pop(index)
            else:
                self.data['portfolio'].pop(index)
            
            self.save_json()
            self.refresh_list()

    def add_item_popup(self):
        self.open_editor(None, None)

    def edit_item_popup(self, item, index):
        self.open_editor(item, index)

    def open_editor(self, item, index):
        top = ctk.CTkToplevel(self)
        top.title(f"{'Edit' if item else 'Add'} {self.mode.capitalize()}")
        top.geometry("500x600")
        top.attributes("-topmost", True)

        # Common Fields
        v_title = ctk.StringVar(value=item.get('name' if self.mode == 'store' else 'title', '') if item else "")
        v_img_path = ctk.StringVar(value=item.get('image', '') if item else "")
        
        # Product Specifics
        v_price = ctk.StringVar(value=item.get('price', '') if item else "")
        v_desc = ctk.StringVar(value=item.get('description', '') if item else "")
        v_code = ctk.StringVar(value=item.get('whatsappCode', '') if item else "")

        def select_image():
            file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
            if file_path:
                filename = os.path.basename(file_path)
                target_dir = IMAGE_DIR if self.mode == 'store' else PORTFOLIO_DIR
                dest = os.path.join(target_dir, filename)
                
                if not os.path.exists(dest):
                    shutil.copy(file_path, dest)
                
                # Store relative path
                rel_path = f"{target_dir}/{filename}".replace("\\", "/") 
                v_img_path.set(rel_path)

        def save():
            new_item = {}
            if self.mode == 'store':
                new_item = {
                    "id": item['id'] if item else str(int(time.time())),
                    "name": v_title.get(),
                    "price": v_price.get(),
                    "description": v_desc.get(),
                    "whatsappCode": v_code.get(),
                    "image": v_img_path.get(),
                    "featured": item.get('featured', False) if item else False
                }
                cat = next((c for c in self.data['categories'] if c['id'] == self.current_selection_id), None)
                if index is not None: cat['products'][index] = new_item
                else: cat['products'].append(new_item)
            else:
                new_item = {
                    "id": item['id'] if item else str(int(time.time())),
                    "title": v_title.get(),
                    "image": v_img_path.get()
                }
                if index is not None: self.data['portfolio'][index] = new_item
                else: self.data['portfolio'].append(new_item)

            self.save_json()
            self.refresh_list()
            top.destroy()

        # UI Construction
        ctk.CTkLabel(top, text="Title / Name").pack(pady=(10,0))
        ctk.CTkEntry(top, textvariable=v_title).pack(pady=5, padx=20, fill="x")

        if self.mode == 'store':
            ctk.CTkLabel(top, text="Price (₹)").pack(pady=(10,0))
            ctk.CTkEntry(top, textvariable=v_price).pack(pady=5, padx=20, fill="x")
            
            ctk.CTkLabel(top, text="Description").pack(pady=(10,0))
            ctk.CTkEntry(top, textvariable=v_desc).pack(pady=5, padx=20, fill="x")
            
            ctk.CTkLabel(top, text="WhatsApp Code").pack(pady=(10,0))
            ctk.CTkEntry(top, textvariable=v_code).pack(pady=5, padx=20, fill="x")

        ctk.CTkLabel(top, text="Image").pack(pady=(10,0))
        img_frame = ctk.CTkFrame(top, fg_color="transparent")
        img_frame.pack(fill="x", padx=20)
        ctk.CTkEntry(img_frame, textvariable=v_img_path).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(img_frame, text="📂 Upload", width=60, command=select_image).pack(side="right", padx=(5,0))

        ctk.CTkButton(top, text="SAVE", fg_color=THEME_COLOR, height=40, command=save).pack(pady=30, padx=20, fill="x")

if __name__ == "__main__":
    app = ProductEditorApp()
    app.mainloop()