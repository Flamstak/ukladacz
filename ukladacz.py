import os
import shutil
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog

CONFIG_FILE = "config.json"
UNDO_LOG_FILE = "undo.log"

def get_unique_filename(dest_folder, filename, claimed_names_in_run=None):
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(dest_folder, unique_filename)) or \
          (claimed_names_in_run is not None and unique_filename in claimed_names_in_run):
        unique_filename = f"{base} ({counter}){ext}"
        counter += 1
    return unique_filename

def get_default_rules():
    return {
        "wideo": [".mp4", ".mov", ".mkv"], "dzwieki": [".mp3"],
        "zdjecia": [".png", ".jpg", ".webp", ".jpeg"], "pdf": [".pdf"],
        "tekst": [".txt"], "photoshop": [".psd"],
        "word": [".doc", ".docx", ".odt"], "excel": [".xls", ".xlsx", ".csv"],
        "archiwum": [".zip", ".rar", ".7z", ".tar", ".gz"]
    }

def load_settings():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if "rules" not in config: config["rules"] = get_default_rules()
            if "default_path" not in config:
                config["default_path"] = os.path.join(os.path.expanduser("~"), "Downloads")
            return config
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "default_path": os.path.join(os.path.expanduser("~"), "Downloads"),
            "rules": get_default_rules()
        }

def save_settings(settings):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except IOError as e:
        messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać ustawień do pliku config.json:\n{e}")

class RulesEditorWindow(ctk.CTkToplevel):
    def __init__(self, master, config):
        super().__init__(master)
        self.transient(master); self.grab_set()
        self.title("Edytor Reguł i Ustawienia"); self.geometry("800x600")
        self.main_app = master; self.config = config
        self.rules = config.get("rules", {}); self.selected_category = None
        self.selected_extension = None; self.category_buttons = {}
        self.extension_buttons = {}
        self.grid_columnconfigure(0, weight=1, minsize=200)
        self.grid_columnconfigure(1, weight=2); self.grid_rowconfigure(1, weight=1)
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.path_frame.grid_columnconfigure(1, weight=1)
        self.label = ctk.CTkLabel(self.path_frame, text="Domyślna ścieżka:")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.path_entry = ctk.CTkEntry(self.path_frame, width=350)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.path_entry.insert(0, self.config.get("default_path", ""))
        self.browse_button = ctk.CTkButton(self.path_frame, text="Przeglądaj...", command=self.browse_path)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)
        self.category_frame = ctk.CTkFrame(self)
        self.category_frame.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.category_frame.grid_rowconfigure(1, weight=1); self.category_frame.grid_columnconfigure(0, weight=1)
        self.category_label = ctk.CTkLabel(self.category_frame, text="Kategorie (Foldery)", font=("", 16, "bold"))
        self.category_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.category_scroll_frame = ctk.CTkScrollableFrame(self.category_frame)
        self.category_scroll_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.cat_add_button = ctk.CTkButton(self.category_frame, text="Dodaj", command=self.add_category)
        self.cat_add_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.cat_del_button = ctk.CTkButton(self.category_frame, text="Usuń", command=self.delete_category)
        self.cat_del_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.ext_frame = ctk.CTkFrame(self)
        self.ext_frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.ext_frame.grid_rowconfigure(1, weight=1); self.ext_frame.grid_columnconfigure(0, weight=1)
        self.ext_label = ctk.CTkLabel(self.ext_frame, text="Wybierz kategorię", font=("", 16, "bold"))
        self.ext_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.ext_scroll_frame = ctk.CTkScrollableFrame(self.ext_frame)
        self.ext_scroll_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.ext_add_button = ctk.CTkButton(self.ext_frame, text="Dodaj", command=self.add_extension)
        self.ext_add_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.ext_del_button = ctk.CTkButton(self.ext_frame, text="Usuń", command=self.delete_extension)
        self.ext_del_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.save_button = ctk.CTkButton(self, text="Zapisz Zmiany i Zamknij", command=self.save_and_close, height=40)
        self.save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.update_category_listbox(); self.update_extension_listbox()
    def update_category_listbox(self):
        for widget in self.category_scroll_frame.winfo_children(): widget.destroy()
        self.category_buttons.clear()
        sorted_categories = sorted(self.rules.keys())
        for category in sorted_categories:
            btn = ctk.CTkButton(self.category_scroll_frame, text=category, fg_color="transparent", anchor="w", command=lambda c=category: self.on_category_select(c))
            btn.pack(fill="x", padx=5, pady=2); self.category_buttons[category] = btn
        self.highlight_selected_category()
    def highlight_selected_category(self):
        for category, button in self.category_buttons.items():
            button.configure(fg_color=("gray75", "gray25") if category == self.selected_category else "transparent")
    def on_category_select(self, category_name):
        self.selected_category = category_name; self.selected_extension = None
        self.highlight_selected_category(); self.update_extension_listbox()
    def update_extension_listbox(self):
        for widget in self.ext_scroll_frame.winfo_children(): widget.destroy()
        self.extension_buttons.clear()
        if self.selected_category and self.selected_category in self.rules:
            self.ext_label.configure(text=f"Rozszerzenia dla: {self.selected_category}")
            sorted_extensions = sorted(self.rules[self.selected_category])
            for ext in sorted_extensions:
                btn = ctk.CTkButton(self.ext_scroll_frame, text=ext, fg_color="transparent", anchor="w", command=lambda e=ext: self.on_extension_select(e))
                btn.pack(fill="x", padx=5, pady=2); self.extension_buttons[ext] = btn
        else: self.ext_label.configure(text="Wybierz kategorię")
        self.highlight_selected_extension()
    def on_extension_select(self, ext_name):
        self.selected_extension = ext_name; self.highlight_selected_extension()
    def highlight_selected_extension(self):
        for ext, button in self.extension_buttons.items():
            button.configure(fg_color=("gray75", "gray25") if ext == self.selected_extension else "transparent")
    def add_category(self):
        dialog = ctk.CTkInputDialog(text="Wpisz nazwę nowej kategorii (folderu):", title="Dodaj Kategorię")
        new_category = dialog.get_input()
        if new_category:
            new_category = new_category.strip()
            if not new_category: return
            if new_category in self.rules: messagebox.showwarning("Błąd", "Kategoria o tej nazwie już istnieje.", parent=self)
            else:
                self.rules[new_category] = []
                self.main_app.log_message(f"[+] Dodano nową kategorię: '{new_category}'", tag="success")
                self.selected_category = new_category
                self.update_category_listbox(); self.update_extension_listbox()
    def add_extension(self):
        if not self.selected_category: messagebox.showwarning("Błąd", "Najpierw wybierz kategorię.", parent=self); return
        dialog = ctk.CTkInputDialog(text=f"Wpisz nowe rozszerzenie (np. .jpg):", title="Dodaj Rozszerzenie")
        new_ext = dialog.get_input()
        if new_ext:
            new_ext = new_ext.strip().lower()
            if not new_ext.startswith("."): new_ext = "." + new_ext
            if new_ext in self.rules[self.selected_category]: messagebox.showwarning("Błąd", "To rozszerzenie już istnieje w tej kategorii.", parent=self)
            else:
                self.rules[self.selected_category].append(new_ext)
                self.main_app.log_message(f"[+] Dodano rozszerzenie '{new_ext}' do kategorii '{self.selected_category}'", tag="success")
                self.selected_extension = new_ext; self.update_extension_listbox()
    def delete_category(self):
        if not self.selected_category: messagebox.showwarning("Błąd", "Najpierw kliknij na kategorię do usunięcia.", parent=self); return
        if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć kategorię '{self.selected_category}'?", parent=self):
            deleted_category = self.selected_category; del self.rules[deleted_category]
            self.main_app.log_message(f"[-] Usunięto kategorię: '{deleted_category}'", tag="warning")
            self.selected_category = None; self.selected_extension = None
            self.update_category_listbox(); self.update_extension_listbox()
    def delete_extension(self):
        if not self.selected_category: messagebox.showwarning("Błąd", "Najpierw wybierz kategorię.", parent=self); return
        if not self.selected_extension: messagebox.showwarning("Błąd", "Najpierw kliknij na rozszerzenie do usunięcia.", parent=self); return
        if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć '{self.selected_extension}' z '{self.selected_category}'?", parent=self):
            self.rules[self.selected_category].remove(self.selected_extension)
            self.main_app.log_message(f"[-] Usunięto rozszerzenie '{self.selected_extension}' z kategorii '{self.selected_category}'", tag="warning")
            self.selected_extension = None; self.update_extension_listbox()
    def browse_path(self):
        folder_selected = filedialog.askdirectory(initialdir=self.path_entry.get())
        if folder_selected: self.path_entry.delete(0, "end"); self.path_entry.insert(0, folder_selected)
    def save_and_close(self):
        new_path = self.path_entry.get()
        if not os.path.isdir(new_path): messagebox.showwarning("Nieprawidłowa ścieżka", "Wybrana ścieżka domyślna nie jest prawidłowym folderem.", parent=self); return
        self.config["default_path"] = new_path; self.config["rules"] = self.rules
        save_settings(self.config); self.main_app.update_default_path_label(new_path)
        self.main_app.config = self.config
        self.main_app.log_message(f"[OK] Zapisano nowe ustawienia i reguły.", tag="success"); self.destroy()

class FileSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sorter Plików"); self.geometry("900x600")
        ctk.set_appearance_mode("system")
        self.config = load_settings(); self.default_path = self.config.get("default_path", "")
        self.rules_editor_window = None; self.active_button = None

        self.grid_columnconfigure(0, weight=1, minsize=300); self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(1, weight=0)

        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="Sorter Plików", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.view_switcher = ctk.CTkSegmentedButton(self.sidebar_frame, values=["Domyślne", "Jednorazowe"], command=self.switch_view)
        self.view_switcher.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.view_switcher.set("Domyślne")

        self.default_sort_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.default_sort_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
        self.default_sort_frame.grid_columnconfigure(0, weight=1)
        self.default_path_label_info = ctk.CTkLabel(self.default_sort_frame, text="Folder domyślny:")
        self.default_path_label_info.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.default_path_label = ctk.CTkLabel(self.default_sort_frame, text=self.default_path, font=("", 12, "italic"), text_color="gray", wraplength=260)
        self.default_path_label.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.custom_sort_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.custom_sort_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ew")
        self.custom_sort_frame.grid_columnconfigure(0, weight=1)
        self.custom_path_label = ctk.CTkLabel(self.custom_sort_frame, text="Wybierz folder:")
        self.custom_path_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.path_entry = ctk.CTkEntry(self.custom_sort_frame, placeholder_text="Wybierz ścieżkę...")
        self.path_entry.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.browse_button = ctk.CTkButton(self.custom_sort_frame, text="Przeglądaj...", command=self.browse_folder)
        self.browse_button.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.action_buttons_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.action_buttons_frame.grid(row=3, column=0, padx=0, pady=0, sticky="ew")
        self.action_buttons_frame.grid_columnconfigure(0, weight=1)
        self.sort_button = ctk.CTkButton(self.action_buttons_frame, text="Uruchom Sortowanie", height=40, command=self.start_sort)
        self.sort_button.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.preview_button = ctk.CTkButton(self.action_buttons_frame, text="Uruchom Podgląd", fg_color="gray", hover_color="gray25", command=self.start_preview)
        self.preview_button.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.separator1 = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray25")
        self.separator1.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.options_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.options_frame.grid(row=5, column=0, padx=0, pady=0, sticky="ew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.recursive_checkbox = ctk.CTkCheckBox(self.options_frame, text="Sortuj rekursywnie (w podfolderach)")
        self.recursive_checkbox.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")
        self.cleanup_checkbox = ctk.CTkCheckBox(self.options_frame, text="Usuń puste podfoldery po sortowaniu")
        self.cleanup_checkbox.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.undo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.undo_frame.grid(row=7, column=0, padx=0, pady=0, sticky="ew")
        self.undo_frame.grid_columnconfigure(0, weight=1)
        self.undo_button = ctk.CTkButton(self.undo_frame, text="Cofnij ostatnią operację", fg_color="#E74C3C", hover_color="#C0392B", command=self.start_undo, state="disabled")
        self.undo_button.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        self.undo_label = ctk.CTkLabel(self.undo_frame, text="Nie ma operacji do cofnięcia", font=("", 12, "italic"), text_color="gray")
        self.undo_label.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="Tryb Ciemny", command=self.toggle_theme)
        self.theme_switch.grid(row=9, column=0, padx=20, pady=10, sticky="s")
        current_mode = ctk.get_appearance_mode(); self.theme_switch.select() if current_mode == "Dark" else self.theme_switch.deselect()
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="Ustawienia i Edytor Reguł", command=self.open_rules_editor)
        self.settings_button.grid(row=10, column=0, padx=20, pady=(5, 20), sticky="s")

        self.log_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.log_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.log_frame.grid_rowconfigure(1, weight=1); self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_label = ctk.CTkLabel(self.log_frame, text="Dziennik Zdarzeń", font=ctk.CTkFont(size=20, weight="bold"))
        self.log_label.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="w")
        self.log_textbox = ctk.CTkTextbox(self.log_frame, state="disabled", wrap="word", font=("", 13))
        self.log_textbox.grid(row=1, column=0, sticky="nsew")

        self.footer_label = ctk.CTkLabel(self, text="Sorter Plików by Flamstak", font=ctk.CTkFont(size=11), text_color=("gray50", "gray50"))
        self.footer_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")

        self.log_textbox.tag_config("success", foreground="#2ECC71"); self.log_textbox.tag_config("warning", foreground="#F39C12")
        self.log_textbox.tag_config("error",   foreground="#E74C3C"); self.log_textbox.tag_config("header",  foreground="#3498DB")
        
        self.switch_view("Domyślne"); self.enable_buttons()

    def switch_view(self, selected_view):
        if selected_view == "Domyślne": self.custom_sort_frame.grid_remove(); self.default_sort_frame.grid()
        elif selected_view == "Jednorazowe": self.default_sort_frame.grid_remove(); self.custom_sort_frame.grid()
    def toggle_theme(self):
        if self.theme_switch.get() == 1: ctk.set_appearance_mode("dark")
        else: ctk.set_appearance_mode("light")
    def log_message(self, message, tag="info"):
        self.after(0, self._update_log_textbox, message, tag)
    def _update_log_textbox(self, message, tag):
        self.log_textbox.configure(state="normal")
        if tag == "info": self.log_textbox.insert("end", f"{message}\n")
        else: self.log_textbox.insert("end", f"{message}\n", (tag,))
        self.log_textbox.configure(state="disabled"); self.log_textbox.see("end")
    def browse_folder(self):
        initial_dir = self.path_entry.get() or self.default_path
        folder_selected = filedialog.askdirectory(initialdir=initial_dir)
        if folder_selected: self.path_entry.delete(0, "end"); self.path_entry.insert(0, folder_selected)
    def open_rules_editor(self):
        if self.rules_editor_window is None or not self.rules_editor_window.winfo_exists():
            self.rules_editor_window = RulesEditorWindow(self, self.config)
        else: self.rules_editor_window.focus()
    def update_default_path_label(self, new_path):
        self.default_path = new_path; self.default_path_label.configure(text=self.default_path)
    def start_sort(self):
        selected_view = self.view_switcher.get()
        if selected_view == "Domyślne": self.active_button = self.sort_button; self.start_sorting_thread(self.default_path, is_preview=False)
        elif selected_view == "Jednorazowe":
            sciezka = self.path_entry.get()
            if not sciezka: messagebox.showerror("Brak ścieżki", "Najpierw wybierz folder do posortowania."); return
            self.active_button = self.sort_button; self.start_sorting_thread(sciezka, is_preview=False)
    def start_preview(self):
        selected_view = self.view_switcher.get()
        if selected_view == "Domyślne": self.active_button = self.preview_button; self.start_sorting_thread(self.default_path, is_preview=True)
        elif selected_view == "Jednorazowe":
            sciezka = self.path_entry.get()
            if not sciezka: messagebox.showerror("Brak ścieżki", "Najpierw wybierz folder do podglądu."); return
            self.active_button = self.preview_button; self.start_sorting_thread(sciezka, is_preview=True)
    def start_sorting_thread(self, sciezka, is_preview=False):
        if not os.path.isdir(sciezka): messagebox.showerror("Błąd", f"Ścieżka '{sciezka}' nie jest prawidłowym folderem."); return
        is_recursive_sort = bool(self.recursive_checkbox.get())
        is_cleanup_enabled = bool(self.cleanup_checkbox.get())
        if is_recursive_sort:
            action_name = "PODGLĄD REKURSYWNY" if is_preview else "SORTOWANIE REKURSYWNE"
            confirmation_message = (f"Czy na pewno chcesz uruchomić {action_name}?\n\n...") 
            if not messagebox.askyesno(f"Uwaga! {action_name}", confirmation_message, parent=self): self.log_message(f"[!!] Anulowano {action_name}.", tag="warning"); return
        self.log_textbox.configure(state="normal"); self.log_textbox.delete("1.0", "end"); self.log_textbox.configure(state="disabled")
        log_start_msg = "[>>] Rozpoczynam PODGLĄD" if is_preview else "[>>] Rozpoczynam SORTOWANIE"
        self.log_message(f"{log_start_msg} w: {sciezka}", tag="header")
        if not is_preview:
            self.log_message("[>>] Czyszczenie dziennika cofania...", tag="info")
            try:
                with open(UNDO_LOG_FILE, 'w', encoding='utf-8') as f: f.write("")
                self.undo_button.configure(state="disabled"); self.undo_label.configure(text="Nie ma operacji do cofnięcia")
            except Exception as e:
                self.log_message(f"[ERR] Nie można wyczyścić pliku cofania: {e}", tag="error")
                messagebox.showerror("Błąd", f"Nie można wyczyścić pliku {UNDO_LOG_FILE}.\nAnulowanie operacji."); return
        if is_recursive_sort: self.log_message("[i] Sortowanie rekursywne: WŁĄCZONE", tag="warning")
        if is_cleanup_enabled:
            log_cleanup_msg = "[i] Podgląd czyszczenia" if is_preview else "[i] Czyszczenie"
            self.log_message(f"{log_cleanup_msg} pustych folderów: WŁĄCZONE", tag="warning")
        self.disable_all_buttons()
        if self.active_button: self.active_button.configure(text="Przetwarzanie...")
        sort_thread = threading.Thread(target=self.run_sorting_logic, args=(sciezka, self.config["rules"], is_recursive_sort, is_preview, is_cleanup_enabled), daemon=True)
        sort_thread.start()
    def start_undo(self):
        if not messagebox.askyesno("Potwierdź Cofanie", "Czy na pewno chcesz cofnąć ostatnią operację sortowania?\n\n...", parent=self): return 
        self.log_textbox.configure(state="normal"); self.log_textbox.delete("1.0", "end"); self.log_textbox.configure(state="disabled")
        self.log_message("[<<] Rozpoczynam operację COFANIA...", tag="header")
        self.disable_all_buttons(); self.active_button = self.undo_button
        self.active_button.configure(text="Cofanie w toku...")
        undo_thread = threading.Thread(target=self.run_undo_logic, daemon=True)
        undo_thread.start()

    def run_sorting_logic(self, sciezka, rules, is_recursive, is_preview, is_cleanup_enabled):
        try:
            extension_map = {ext.lower(): cat for cat, exts in rules.items() for ext in exts}
            log_prefix = "[P] Podgląd: " if is_preview else ""
            log_folder_verb = "zostałby utworzony" if is_preview else "Utworzono"
            log_move_verb = "zostałby przeniesiony" if is_preview else "Przeniesiono"
            log_rename_verb = "miałaby zmienioną nazwę" if is_preview else "miała zmienioną nazwę"

            self.log_message(f"{log_prefix}[>>] Sprawdzanie/tworzenie folderów docelowych...", tag="info")
            category_folders = set(rules.keys())
            category_folder_paths = set(os.path.normpath(os.path.join(sciezka, f)) for f in category_folders)
            for folder_path in category_folder_paths:
                if not os.path.exists(folder_path):
                    if not is_preview: os.makedirs(folder_path); self.log_message(f" 	[++] {log_folder_verb} folder: '{os.path.basename(folder_path)}'", tag="success")
                    else: self.log_message(f" 	{log_prefix}[++] Folder '{os.path.basename(folder_path)}' {log_folder_verb}.", tag="info")
            moved_per_folder = { folder: 0 for folder in category_folders }
            total_moved, duplicates, unhandled_files, already_sorted_files = 0, 0, 0, 0
            duplicates_list = []; files_to_process = []; claimed_names_in_run = set()
            scan_type = "rekursywne (wszystkie podfoldery)" if is_recursive else "folderu głównego"
            self.log_message(f"{log_prefix}[>>] Skanowanie {scan_type}...", tag="info")
            if is_recursive:
                for root, dirs, files in os.walk(sciezka, topdown=True):
                    for filename in files: files_to_process.append((os.path.join(root, filename), filename))
            else:
                for filename in os.listdir(sciezka):
                    full_path = os.path.join(sciezka, filename)
                    if os.path.isfile(full_path): files_to_process.append((full_path, filename))
            self.log_message(f"{log_prefix}[i] Znaleziono {len(files_to_process)} plików. Rozpoczynam przetwarzanie...", tag="info")
            for pelna_sciezka, i in files_to_process:
                filename, file_ext = os.path.splitext(i); file_ext_lower = file_ext.lower()
                dest_folder_name = extension_map.get(file_ext_lower)
                if dest_folder_name is not None:
                    dest_folder_path = os.path.join(sciezka, dest_folder_name)
                    source_directory = os.path.dirname(pelna_sciezka)
                    relative_source_dir = os.path.relpath(source_directory, sciezka)
                    if relative_source_dir == '.': relative_source_dir = "(folder główny)" 

                    if os.path.normpath(source_directory) == os.path.normpath(dest_folder_path): already_sorted_files += 1; continue
                    unique_name = get_unique_filename(dest_folder_path, i, claimed_names_in_run)
                    claimed_names_in_run.add(unique_name)
                    if unique_name != i: duplicates += 1; duplicates_list.append(f"'{i}' -> '{unique_name}' (z '{relative_source_dir}')") 

                    if not is_preview:
                        try:
                            final_dest_path = os.path.join(dest_folder_path, unique_name)
                            log_entry = {"type": "move", "from": pelna_sciezka, "to": final_dest_path}
                            with open(UNDO_LOG_FILE, 'a', encoding='utf-8') as f: f.write(json.dumps(log_entry) + '\n')
                            shutil.move(pelna_sciezka, final_dest_path)
                            total_moved += 1; moved_per_folder[dest_folder_name] += 1
                            log_msg = f"[->] Przeniesiono '{i}' z '{relative_source_dir}'"
                            if unique_name != i: log_msg += f" jako '{unique_name}'"
                            log_msg += f" do '{dest_folder_name}'"
                            self.log_message(log_msg, tag="success")
                        except Exception as e: self.log_message(f"[ERR] BŁĄD przy przenoszeniu pliku '{i}' z '{relative_source_dir}': {e}", tag="error") 
                    else:
                        total_moved += 1; moved_per_folder[dest_folder_name] += 1
                        log_msg = f"{log_prefix}[->] Plik '{i}' z '{relative_source_dir}' {log_move_verb}"
                        if unique_name != i: log_msg += f" jako '{unique_name}'"
                        log_msg += f" do folderu '{dest_folder_name}'"
                        self.log_message(log_msg, tag="info")
                else: unhandled_files += 1
            summary_header = "[P] PODGLĄD ZAKOŃCZONY" if is_preview else "[OK] SORTOWANIE ZAKOŃCZONE"
            summary_moved_verb = "Znaleziono" if is_preview else "Przeniesiono"
            self.log_message(f"\n--- {summary_header} ---", tag="header")
            self.log_message(f"[OK] {summary_moved_verb} {total_moved} plików.", tag="success")
            if unhandled_files > 0: self.log_message(f"[i] Pominięto {unhandled_files} plików (nie pasowały do żadnej reguły).")
            if already_sorted_files > 0: self.log_message(f"[i] Pominięto {already_sorted_files} plików (były już w swoim folderze docelowym).")
            if duplicates > 0: self.log_message(f"[!!] {duplicates} plików {log_rename_verb} z powodu konfliktu nazw.", tag="warning")
            else: self.log_message(f"[i] Nie wykryto konfliktów nazw.")
            if duplicates_list: self.log_message(f"\n[!!] Pliki, które {log_rename_verb}:", tag="warning"); [self.log_message(f" 	{item}", tag="warning") for item in duplicates_list]
            self.log_message("\n[i] Podsumowanie folderów docelowych:"); [self.log_message(f" 	+ '{f}': {c} plików") for f, c in moved_per_folder.items() if c > 0]
            if is_cleanup_enabled:
                cleanup_header = f"--- {log_prefix}🧹 ANALIZA PUSTYCH FOLDERÓW ---" if is_preview else "--- 🧹 ROZPOCZYNAM CZYSZCZENIE ---"
                cleanup_log_msg = f"{log_prefix}[>>] Wyszukiwanie pustych podfolderów..."
                self.log_message(f"\n{cleanup_header}", tag="header"); self.log_message(cleanup_log_msg, tag="info")
                deleted_count = 0; norm_sciezka = os.path.normpath(sciezka)
                for root, dirs, files in os.walk(sciezka, topdown=False):
                    norm_root = os.path.normpath(root)
                    if norm_root == norm_sciezka: continue
                    if norm_root in category_folder_paths: continue
                    try:
                        is_empty = not os.listdir(root) 
                        if is_empty:
                            if not is_preview:
                                log_entry = {"type": "rmdir", "path": root}
                                with open(UNDO_LOG_FILE, 'a', encoding='utf-8') as f: f.write(json.dumps(log_entry) + '\n')
                                os.rmdir(root); self.log_message(f" 	[-] Usunięto pusty folder: {root}", tag="success")
                            else:
                                self.log_message(f" 	{log_prefix}[-] Pusty folder '{root}' *zostałby* usunięty.", tag="info")
                            deleted_count += 1
                    except OSError as e: self.log_message(f"[ERR] BŁĄD: Nie można przeanalizować/usunąć folderu {root}: {e}", tag="error")

                cleanup_summary_verb = "Znaleziono" if is_preview else "Usunięto"
                if deleted_count > 0:
                    self.log_message(f"{log_prefix}[OK] {cleanup_summary_verb} {deleted_count} pustych folderów.", tag="success")
                else:
                    if is_preview:
                        self.log_message(f"{log_prefix}[i] Nie znaleziono folderów, które są puste PRZED symulowanym sortowaniem.", tag="info")
                        self.log_message(f"{log_prefix}[i] Rzeczywista liczba usuniętych folderów po sortowaniu może być większa.", tag="info")
                    else:
                        self.log_message(f"{log_prefix}[i] Nie znaleziono żadnych pustych podfolderów do usunięcia.")

        except Exception as e:
            self.log_message(f"\n--- [ERR] KRYTYCZNY BŁĄD ---", tag="error"); self.log_message(f"Błąd: {e}", tag="error")
            messagebox.showerror("Błąd krytyczny", f"Wystąpił nieoczekiwany błąd:\n{e}")
        finally: self.after(0, self.enable_buttons)

    def run_undo_logic(self):
        try:
            if not os.path.exists(UNDO_LOG_FILE): self.log_message("[ERR] BŁĄD: Plik dziennika cofania nie istnieje.", tag="error"); return
            with open(UNDO_LOG_FILE, 'r', encoding='utf-8') as f: log_lines = f.readlines()
            if not log_lines: self.log_message("[!!] Dziennik cofania jest pusty. Nic do zrobienia.", tag="warning"); return

            log_entries = [json.loads(line) for line in log_lines if line.strip()]; log_entries.reverse()
            self.log_message(f"[>>] Znaleziono {len(log_entries)} operacji do cofnięcia. Rozpoczynam...", tag="info")
            total_undone = 0; undone_files = 0; recreated_folders = 0

            for entry in log_entries:
                try:
                    if entry["type"] == "move":
                        original_source_dir = os.path.dirname(entry["from"])
                        if not os.path.exists(original_source_dir):
                            os.makedirs(original_source_dir, exist_ok=True); self.log_message(f" 	[++] Odtworzono brakujący folder: {original_source_dir}", tag="info")
                        shutil.move(entry["to"], entry["from"])
                        self.log_message(f" 	[<-] Przywrócono plik '{os.path.basename(entry['from'])}' do '{original_source_dir}'", tag="success"); undone_files += 1 
                    elif entry["type"] == "rmdir":
                        os.makedirs(entry["path"], exist_ok=True); self.log_message(f" 	[++] Odtworzono usunięty folder: {entry['path']}", tag="success"); recreated_folders +=1
                    total_undone += 1
                except Exception as e: self.log_message(f"[ERR] BŁĄD podczas cofania operacji ({entry}): {e}", tag="error")

            self.log_message(f"\n--- [OK] COFANIE ZAKOŃCZONE ---", tag="header")
            self.log_message(f"[OK] Pomyślnie cofnięto {undone_files} plików i odtworzono {recreated_folders} folderów.", tag="success")
            os.remove(UNDO_LOG_FILE)
        except Exception as e:
            self.log_message(f"\n--- [ERR] KRYTYCZNY BŁĄD PODCZAS COFANIA ---", tag="error"); self.log_message(f"Błąd: {e}", tag="error")
            messagebox.showerror("Błąd krytyczny", f"Wystąpił nieoczekiwany błąd podczas cofania:\n{e}")
        finally: self.after(0, self.enable_buttons)

    def disable_all_buttons(self):
        self.sort_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        self.undo_button.configure(state="disabled")

    def enable_buttons(self):
        self.sort_button.configure(state="normal", text="Uruchom Sortowanie")
        self.preview_button.configure(state="normal", text="Uruchom Podgląd")
        self.active_button = None
        try:
            can_undo = os.path.exists(UNDO_LOG_FILE) and os.path.getsize(UNDO_LOG_FILE) > 0
            self.undo_button.configure(state="normal" if can_undo else "disabled", text="Cofnij ostatnią operację")
            self.undo_label.configure(text="Ostatnia operacja gotowa do cofnięcia" if can_undo else "Nie ma operacji do cofnięcia")
        except Exception:
            self.undo_button.configure(state="disabled", text="Cofnij ostatnią operację")
            self.undo_label.configure(text="Nie ma operacji do cofnięcia")

if __name__ == "__main__":
    app = FileSorterApp()
    app.mainloop()