# Tile Counter - Android edition
# Converted from the original Tkinter app to Kivy for Android packaging.

import os
import json
import csv
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

BRANDS = [
    "Virony", "Royal / Royal Ceramic", "Royal Castle", "Goodwill",
    "CDK", "BN Ceramics", "Ceramco", "Time Ceramics",
    "Sapphire Ceramics", "Yaqout",
]
DESIGNS = [
    "Porcelain Tiles", "Ceramic Tiles",
    "Vitrified Tiles (incl. Double-Charged)", "Super Polished / Polished",
    "Glazed Tiles", "Rustic / Matt / Anti-Slip", "Marble",
]
SIZES = [
    "Wall Tile — 25 × 40 cm", "Wall Tile — 30 × 60 cm",
    "Floor Tile (Ceramic) — 30 × 30 cm", "Floor Tile (Ceramic) — 40 × 40 cm",
    "Floor Tile — 60 × 60 cm", "Floor Tile (Porcelain) — 30 × 60 cm",
    "Porcelain Tile — 60 × 120 cm", "Outdoor Tile — 30 × 30 cm",
]
COLORS = [
    ("White", "#F8FAFC"), ("Cream / Beige", "#E7D8B8"), ("Grey", "#9CA3AF"),
    ("Dark Grey", "#4B5563"), ("Black", "#111827"), ("Brown", "#92400E"),
    ("Blue", "#2563EB"), ("Green", "#16A34A"), ("Red", "#DC2626"),
    ("Gold", "#CA8A04"), ("Marble White", "#E5E7EB"), ("Multi-colour", "#A855F7"),
]

BG = "#0F172A"
CARD = "#1E293B"
CARD2 = "#334155"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
ACCENT = "#F59E0B"
GREEN = "#16A34A"
RED = "#DC2626"
BLUE = "#2563EB"
GREY = "#475569"
ORANGE = "#D97706"


def rgba(hex_color):
    return get_color_from_hex(hex_color)


def readable_text(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16)
    return "#000000" if (0.299*r + 0.587*g + 0.114*b) > 150 else TEXT


class TileCounterApp(App):
    title = "Tile Counter"

    def build(self):
        Window.clearcolor = rgba(BG)
        self.data_dir = self.user_data_dir
        self.state_file = os.path.join(self.data_dir, "state.json")
        self.records_file = os.path.join(self.data_dir, "records.json")
        self.csv_file = os.path.join(self.data_dir, "tile_records.csv")
        self.sel = {"brand": "", "design": "", "size": "", "color": ""}
        self.count = 0
        self.history = []
        self.carry = [1, 2, 3, 4, 5]
        self.records = []
        self.load_data()
        self.root_box = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        self.show_home()
        return self.root_box

    def label(self, text, size=16, color=TEXT, height=None, halign="center"):
        w = Label(
            text=str(text), font_size=sp(size), color=rgba(color),
            size_hint_y=None if height else 1, height=dp(height) if height else 0,
            halign=halign, valign="middle"
        )
        w.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0]-dp(8), None)))
        return w

    def btn(self, text, callback, color=CARD2, height=48, font_size=16, fg=TEXT):
        b = Button(
            text=str(text), size_hint_y=None, height=dp(height),
            font_size=sp(font_size), color=rgba(fg),
            background_normal="", background_down="", background_color=rgba(color),
        )
        b.bind(on_release=lambda *_: callback())
        return b

    def reset_screen(self):
        self.root_box.clear_widgets()

    def scroll_area(self, parent):
        scroll = ScrollView(do_scroll_x=False)
        parent.add_widget(scroll)
        return scroll

    def load_data(self):
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for key in self.sel:
                self.sel[key] = str(data.get("sel", {}).get(key, ""))
            self.count = max(0, int(data.get("count", 0)))
            self.history = [int(x) for x in data.get("history", [])]
            carry = [int(x) for x in data.get("carry", [])]
            if carry:
                self.carry = sorted(set(carry))
        except (OSError, ValueError, TypeError):
            pass
        try:
            with open(self.records_file, "r", encoding="utf-8") as f:
                self.records = json.load(f)
        except (OSError, ValueError, TypeError):
            self.records = []

    def save_state(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump({"sel": self.sel, "count": self.count,
                           "history": self.history[-200:], "carry": self.carry},
                          f, ensure_ascii=False)
        except OSError:
            self.popup("Save error", "Could not save the current count.")

    def save_records(self):
        try:
            with open(self.records_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            with open(self.csv_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["No", "Date & Time", "Size", "Company",
                                 "Tile type", "Colour", "Tiles counted"])
                for i, r in enumerate(self.records, 1):
                    writer.writerow([i, r["time"], r["size"], r["brand"],
                                     r["design"], r["color"], r["count"]])
        except OSError:
            self.popup("Export error", "Could not write the records CSV file.")

    def popup(self, title, message, buttons=None):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(Label(text=message, color=rgba(TEXT), halign="center", valign="middle"))
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        if buttons:
            for caption, action in buttons:
                b = self.btn(caption, lambda a=action: (pop.dismiss(), a()), GREEN if caption == "Yes" else GREY)
                row.add_widget(b)
        else:
            row.add_widget(self.btn("OK", lambda: pop.dismiss(), BLUE))
        content.add_widget(row)
        pop = Popup(title=title, content=content, size_hint=(0.88, None), height=dp(220), auto_dismiss=False)
        pop.open()
        return pop

    def ask_text(self, title, hint, callback):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8))
        field = TextInput(hint_text=hint, multiline=False, size_hint_y=None, height=dp(48))
        layout.add_widget(field)
        row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        pop = Popup(title=title, content=layout, size_hint=(0.9, None), height=dp(190))
        row.add_widget(self.btn("Cancel", pop.dismiss, GREY))
        def accept():
            value = field.text.strip()
            pop.dismiss()
            if value:
                callback(value)
        row.add_widget(self.btn("Save", accept, GREEN))
        layout.add_widget(row)
        pop.open()

    def show_home(self):
        self.reset_screen()
        self.root_box.add_widget(self.label("TILE COUNTER", 25, ACCENT, 44))
        self.root_box.add_widget(self.label("Choose the tile, then start counting", 13, MUTED, 30))
        scroll = ScrollView(do_scroll_x=False)
        grid = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=(0, dp(3)))
        grid.bind(minimum_height=grid.setter("height"))
        for label, key in [("Company", "brand"), ("Tile type", "design"),
                           ("Size (required)", "size"), ("Colour", "color")]:
            value = self.sel[key] or "(tap to choose)"
            bg = CARD2 if self.sel[key] else CARD
            grid.add_widget(self.btn(f"{label}\n{value}", lambda k=key: self.show_picker(k), bg, 62, 14))
        scroll.add_widget(grid)
        self.root_box.add_widget(scroll)
        start = "CONTINUE COUNTING  (%d)" % self.count if self.count else "START COUNTING"
        self.root_box.add_widget(self.btn(start, self.show_counter, GREEN, 56, 17))
        self.root_box.add_widget(self.btn("SAVED LIST (%d entries)" % len(self.records), self.show_records, BLUE, 48, 15))
        self.root_box.add_widget(self.btn("Clear my choices", self.clear_choices, GREY, 40, 13))

    def clear_choices(self):
        self.sel = {k: "" for k in self.sel}
        self.save_state()
        self.show_home()

    def show_picker(self, key):
        title, items = {
            "brand": ("Choose company", BRANDS),
            "design": ("Choose tile type", DESIGNS),
            "size": ("Choose size", SIZES),
            "color": ("Choose colour", [c[0] for c in COLORS]),
        }[key]
        self.reset_screen()
        self.root_box.add_widget(self.label(title.upper(), 21, ACCENT, 44))
        scroll = ScrollView(do_scroll_x=False)
        grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for item in items:
            grid.add_widget(self.btn(item, lambda v=item: self.choose_value(key, v), CARD2, 48, 14))
        grid.add_widget(self.btn("Other / type manually", lambda: self.ask_text(title, "Enter value", lambda v: self.choose_value(key, v)), BLUE))
        scroll.add_widget(grid)
        self.root_box.add_widget(scroll)
        self.root_box.add_widget(self.btn("< BACK", self.show_home, GREY, 44))

    def choose_value(self, key, value):
        self.sel[key] = value
        self.save_state()
        self.show_home()

    def summary(self):
        return "{}\n{} | {}\nColour: {}".format(
            self.sel["size"], self.sel["brand"] or "-", self.sel["design"] or "-",
            self.sel["color"] or "-")

    def show_counter(self):
        if not self.sel["size"]:
            self.popup("Size needed", "Please choose the tile size first.")
            return
        self.reset_screen()
        self.root_box.add_widget(self.btn(self.summary() + "\n(tap to change)", self.change_tile, CARD, 78, 13))
        self.root_box.add_widget(self.label(str(self.count), 48, ACCENT, 64))
        self.root_box.add_widget(self.label("tiles counted", 13, MUTED, 24))
        cols = 3
        carry_grid = GridLayout(cols=cols, spacing=dp(5), size_hint_y=None)
        carry_grid.bind(minimum_height=carry_grid.setter("height"))
        for n in self.carry:
            carry_grid.add_widget(self.btn("+%d" % n, lambda v=n: self.add(v), BLUE, 55, 22))
        self.root_box.add_widget(carry_grid)
        actions = GridLayout(cols=3, spacing=dp(5), size_hint_y=None, height=dp(54))
        actions.add_widget(self.btn("− 1", lambda: self.add(-1), RED, 54, 18))
        actions.add_widget(self.btn("UNDO", self.undo, ORANGE, 54, 14))
        actions.add_widget(self.btn("Edit +", self.edit_buttons, GREY, 54, 13))
        self.root_box.add_widget(actions)
        save_row = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(58))
        save_row.add_widget(self.btn("SAVE TO LIST", self.save_entry, GREEN, 58, 15))
        save_row.add_widget(self.btn("RESET COUNT", self.confirm_reset, GREY, 58, 13))
        self.root_box.add_widget(save_row)
        foot = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(48))
        foot.add_widget(self.btn("CHANGE TILE", self.change_tile, CARD2, 48, 12))
        foot.add_widget(self.btn("SAVED LIST", self.show_records, CARD2, 48, 12))
        self.root_box.add_widget(foot)

    def add(self, amount):
        if self.count + amount < 0:
            amount = -self.count
        if amount:
            self.count += amount
            self.history.append(amount)
            self.save_state()
            self.show_counter()

    def undo(self):
        if not self.history:
            self.popup("Undo", "Nothing to undo.")
            return
        self.count = max(0, self.count - self.history.pop())
        self.save_state()
        self.show_counter()

    def confirm_reset(self):
        if self.count:
            self.popup("Reset count", "Set the count back to 0? Unsaved count: %d" % self.count,
                       [("Cancel", lambda: None), ("Yes", self.reset_count)])
        else:
            self.reset_count()

    def reset_count(self):
        self.count = 0
        self.history = []
        self.save_state()
        self.show_counter()

    def save_entry(self):
        if self.count <= 0:
            self.popup("Nothing to save", "The count is 0.")
            return
        self.records.append({
            "time": datetime.now().strftime("%d %b %Y  %H:%M"),
            "brand": self.sel["brand"], "design": self.sel["design"],
            "size": self.sel["size"], "color": self.sel["color"], "count": self.count,
        })
        saved = self.count
        self.save_records()
        self.count = 0
        self.history = []
        self.save_state()
        self.popup("Saved", "Saved %d tiles to the list." % saved)
        self.show_counter()

    def change_tile(self):
        if self.count:
            self.popup("Unsaved count", "Save this count before changing tile, or keep counting.",
                       [("Keep counting", self.show_counter), ("Save count", self.save_entry)])
        else:
            self.show_home()

    def edit_buttons(self):
        self.ask_text("Edit + buttons", "Enter number to add or remove", self.apply_carry_edit)

    def apply_carry_edit(self, value):
        try:
            n = int(value)
            if n < 1 or n > 1000:
                raise ValueError
        except ValueError:
            self.popup("Invalid number", "Enter a whole number from 1 to 1000.")
            return
        if n in self.carry:
            if len(self.carry) > 1:
                self.carry.remove(n)
        elif len(self.carry) < 12:
            self.carry.append(n)
            self.carry.sort()
        else:
            self.popup("Too many", "Maximum is 12 + buttons.")
            return
        self.save_state()
        self.show_counter()

    def show_records(self, mode="all"):
        self.reset_screen()
        total = sum(int(r.get("count", 0)) for r in self.records)
        self.root_box.add_widget(self.label("SAVED LIST", 22, ACCENT, 42))
        self.root_box.add_widget(self.label("%d entries | %d tiles in total" % (len(self.records), total), 13, MUTED, 28))
        tabs = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(45))
        tabs.add_widget(self.btn("ALL ENTRIES", lambda: self.show_records("all"), ACCENT if mode == "all" else CARD2, 45, 12, "#000000" if mode == "all" else TEXT))
        tabs.add_widget(self.btn("TOTALS", lambda: self.show_records("totals"), ACCENT if mode == "totals" else CARD2, 45, 12, "#000000" if mode == "totals" else TEXT))
        self.root_box.add_widget(tabs)
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, padding=dp(8))
        content.bind(minimum_height=content.setter("height"))
        if not self.records:
            content.add_widget(self.label("Nothing saved yet.", 15, MUTED, 50))
        elif mode == "all":
            for i, r in reversed(list(enumerate(self.records, 1))):
                text = "#%d  %s\n%s\n%s | %s | %s\n%d tiles" % (
                    i, r["time"], r["size"], r["brand"] or "-", r["design"] or "-",
                    r["color"] or "-", r["count"])
                content.add_widget(self.label(text, 13, TEXT, 94, "left"))
        else:
            by_size, groups = {}, {}
            for r in self.records:
                by_size[r["size"]] = by_size.get(r["size"], 0) + r["count"]
                key = (r["size"], r["brand"], r["design"], r["color"])
                groups[key] = groups.get(key, 0) + r["count"]
            content.add_widget(self.label("TOTAL BY SIZE", 15, ACCENT, 32))
            for size, n in sorted(by_size.items()):
                content.add_widget(self.label("%s\n%d tiles" % (size, n), 13, TEXT, 52, "left"))
            content.add_widget(self.label("DETAIL (same tile added together)", 14, ACCENT, 40))
            for key, n in sorted(groups.items()):
                content.add_widget(self.label("%s\n%s | %s | %s\n%d tiles" % (
                    key[0], key[1] or "-", key[2] or "-", key[3] or "-", n), 13, TEXT, 72, "left"))
        scroll.add_widget(content)
        self.root_box.add_widget(scroll)
        actions = GridLayout(cols=3, spacing=dp(4), size_hint_y=None, height=dp(50))
        actions.add_widget(self.btn("DELETE LAST", lambda: self.delete_last(mode), ORANGE, 50, 11))
        actions.add_widget(self.btn("EXPORT CSV", self.export_csv, BLUE, 50, 11))
        actions.add_widget(self.btn("CLEAR ALL", self.confirm_clear, RED, 50, 11))
        self.root_box.add_widget(actions)
        self.root_box.add_widget(self.btn("< BACK", self.show_home, GREY, 44, 13))

    def delete_last(self, mode):
        if not self.records:
            self.popup("Saved list", "There are no entries to delete.")
            return
        self.popup("Delete last entry", "Delete the most recent saved entry?",
                   [("Cancel", lambda: None), ("Delete", lambda: self._delete_last(mode))])

    def _delete_last(self, mode):
        if self.records:
            self.records.pop()
            self.save_records()
            self.show_records(mode)

    def confirm_clear(self):
        if not self.records:
            return
        self.popup("Clear all", "Delete all %d saved entries? This cannot be undone." % len(self.records),
                   [("Cancel", lambda: None), ("Delete all", self.clear_all)])

    def clear_all(self):
        self.records = []
        self.save_records()
        self.show_records()

    def export_csv(self):
        self.save_records()
        self.popup("CSV exported", "CSV file created at:\n%s\n\nOn Android it is stored in this app's private data folder. Use the project instructions to add a share/save-to-Downloads option if you need a public copy." % self.csv_file)


if __name__ == "__main__":
    TileCounterApp().run()
