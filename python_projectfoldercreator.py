import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import yaml

# Absoluter Pfad zur YAML
source_path = Path(__file__).resolve().parent
YAML_PATH = source_path / "project_structures.yaml"

def load_structures():
    try:
        with open(YAML_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        messagebox.showerror("YAML Fehler", f"Kann YAML nicht laden: {e}")
        return []

def parse_structure_text(text):
    """Parst Strukturtext: (relativer Pfad, ist_dir)"""
    result = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or not line.startswith("#"):
            if line:
                is_dir = line.endswith("/")
                name = line[:-1] if is_dir else line
                result.append((name, is_dir))
    return result

def create_structure(base_path, structure_lines, file_contents=None):
    try:
        for rel_path, is_dir in parse_structure_text(structure_lines):
            p = base_path / rel_path
            if is_dir:
                p.mkdir(parents=True, exist_ok=True)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch(exist_ok=True)
                # Falls Inhalt hinterlegt ist, direkt schreiben
                if file_contents and rel_path in file_contents:
                    p.write_text(file_contents[rel_path], encoding="utf-8")
        return True
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Erstellen: {e}")
        return False

def select_directory():
    path = filedialog.askdirectory(title="Zielordner auswählen")
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)

def on_dropdown_select(event):
    idx = dropdown.current()
    if idx >= 0 and idx < len(structures):
        struct = structures[idx].get("structure", "")
        structure_text.delete("1.0", tk.END)
        structure_text.insert("1.0", struct)

def create_project():
    base_dir = entry_path.get().strip()
    proj_name = entry_name.get().strip()
    tree_text = structure_text.get("1.0", tk.END).strip()
    if not base_dir or not proj_name or not tree_text:
        messagebox.showwarning("Fehlende Eingaben", "Bitte Basisordner, Projektname und Strukturtext angeben!")
        return

    target = Path(base_dir) / proj_name
    target.mkdir(parents=True, exist_ok=True)

    # Zuordnung der Datei-Inhalte aus YAML
    idx = dropdown.current()
    file_contents = {}
    if idx >= 0 and idx < len(structures):
        file_contents = structures[idx].get("files", {})

    success = create_structure(target, tree_text, file_contents)
    if success:
        messagebox.showinfo("Erfolg", f"Projekt '{proj_name}' wurde unter '{target}' erstellt.")

# --- GUI ---
try:
    import ttkbootstrap as ttk
except ImportError:
    import tkinter.ttk as ttk

root = tk.Tk()
root.title("Projektstruktur-GUI mit Datei-Inhalten aus YAML")

tk.Label(root, text="Basisordner:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
entry_path = tk.Entry(root, width=50)
entry_path.grid(row=0, column=1, padx=5)
tk.Button(root, text="Durchsuchen", command=select_directory).grid(row=0, column=2, padx=5)

tk.Label(root, text="Projektname:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
entry_name = tk.Entry(root, width=50)
entry_name.grid(row=1, column=1, padx=5)

tk.Label(root, text="Projektstruktur auswählen:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
structures = load_structures()
dropdown_values = [s["name"] for s in structures]
dropdown = ttk.Combobox(root, values=dropdown_values, state="readonly", width=47)
dropdown.grid(row=2, column=1, padx=5, sticky="w")
dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)
if structures:
    dropdown.current(0)

tk.Label(root, text="Struktur-Text:").grid(row=3, column=0, sticky="nw", padx=5, pady=3)
structure_text = scrolledtext.ScrolledText(root, width=50, height=12)
structure_text.grid(row=3, column=1, columnspan=2, padx=5, pady=3)
if structures:
    structure_text.insert("1.0", structures[0].get("structure", ""))

tk.Button(root, text="Projekt erstellen", command=create_project).grid(row=4, column=1, pady=10)

root.mainloop()
