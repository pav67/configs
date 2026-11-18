"""GTK layer-shell clipboard menu with variable row heights and persistent pins."""
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango, GtkLayerShell
from clipboard_history import content_id, mime_type, run, set_pin
import subprocess


CSS = b'''
window { background: #1e1e2e; color: #cdd6f4; border: 2px solid #585b70; border-radius: 16px; }
.header { font-size: 18px; font-weight: bold; }
entry { background: #313244; color: #cdd6f4; border-radius: 9px; padding: 10px; }
list, scrolledwindow { background: transparent; }
row { padding: 7px 10px; border-radius: 8px; margin: 2px 0; }
row:selected { background: #45475a; }
row:hover { background: #313244; }
button { background: transparent; color: #a6adc8; border: none; box-shadow: none; padding: 5px 9px; }
button:hover { background: #585b70; }
button.pinned { color: #cba6f7; }
.hint { color: #a6adc8; font-size: 12px; }
/* Explicit child colors prevent the system GTK theme from using dark text. */
window label, window entry, window button, window image,
window row:selected label, window row:hover label,
window button:hover label, window button:active label {
    color: #f5f5ff;
    text-shadow: none;
}
window entry selection { color: #ffffff; background: #665484; }
'''


class Picker:
    def __init__(self, entries, pins):
        self.result = None
        self.seen = set()
        self.entries = iter(entries)
        self.loading = True
        self.window = Gtk.Window(title='Presse-papiers')
        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.set_namespace(self.window, 'clipboard-history')
        GtkLayerShell.set_layer(self.window, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self.window, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        display = Gdk.Display.get_default()
        pointer = display.get_default_seat().get_pointer()
        _, x, y = pointer.get_position()
        monitor = display.get_monitor_at_point(x, y)
        if monitor:
            GtkLayerShell.set_monitor(self.window, monitor)
        geometry = monitor.get_geometry() if monitor else None
        height = min(1000, (geometry.height if geometry else 1080) - 100)
        width = min(1000, (geometry.width if geometry else 1920) - 80)
        # Layer-shell uses the widget's minimum requisition, not GtkWindow's
        # default size. Explicitly reserve space for the scrollable viewport.
        self.window.set_size_request(width, height)
        self.window.connect('destroy', lambda *_: Gtk.main_quit())
        self.window.connect('key-press-event', self.keypress)
        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(18)
        self.window.add(box)
        heading = Gtk.Label(label='Presse-papiers', xalign=0)
        heading.get_style_context().add_class('header')
        box.pack_start(heading, False, False, 0)
        self.search = Gtk.SearchEntry(placeholder_text='Rechercher dans les copies et les favoris…')
        self.search.connect('search-changed', self.filter_changed)
        box.pack_start(self.search, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(max(120, height - 190))
        scroll.set_vexpand(True)
        box.pack_start(scroll, True, True, 0)
        self.list = Gtk.ListBox()
        self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list.set_activate_on_single_click(True)
        self.list.set_filter_func(self.matches)
        self.list.set_sort_func(lambda a, b: ((not a.pinned, a.order) > (not b.pinned, b.order)) - ((not a.pinned, a.order) < (not b.pinned, b.order)))
        self.list.connect('row-activated', self.activate)
        scroll.add(self.list)
        self.status = Gtk.Label(xalign=0)
        self.status.set_line_wrap(True)
        self.status.set_max_width_chars(100)
        self.status.get_style_context().add_class('hint')
        box.pack_start(self.status, False, False, 0)
        self.order = 0
        for data in pins:
            self.add(data, True)
        self.window.show_all()
        self.search.grab_focus()
        self.update_status()
        self.source = GLib.idle_add(self.load_batch)

    def add(self, data, pinned=False):
        identity = content_id(data)
        if identity in self.seen:
            return
        self.seen.add(identity)
        row = Gtk.ListBoxRow()
        row.data, row.pinned, row.order = data, pinned, self.order
        self.order += 1
        line = Gtk.Box(spacing=12)
        row.add(line)
        kind = mime_type(data)
        text = data.decode('utf-8', errors='replace') if not kind.startswith('image/') else 'Image ' + kind.split('/')[1].upper()
        row.search_text = text.casefold()
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        content.set_hexpand(True)
        line.pack_start(content, True, True, 0)
        if kind.startswith('image/'):
            try:
                loader = GdkPixbuf.PixbufLoader.new()
                def size_prepared(loader, width, height):
                    scale = min(320 / width, 160 / height, 1)
                    loader.set_size(max(1, int(width * scale)), max(1, int(height * scale)))
                loader.connect('size-prepared', size_prepared)
                loader.write(data)
                loader.close()
                image = Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
                image.set_halign(Gtk.Align.START)
                content.pack_start(image, False, False, 0)
            except GLib.Error:
                text += ' — aperçu indisponible'
        preview = '\n'.join(text[:500].splitlines()[:4]) or '(vide)'
        label = Gtk.Label(label=preview, xalign=0)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_max_width_chars(68)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_lines(4)
        content.pack_start(label, False, False, 0)
        button = Gtk.Button(label='★' if pinned else '☆')
        button.set_valign(Gtk.Align.CENTER)
        button.set_tooltip_text('Désépingler' if pinned else 'Épingler pour conserver')
        button.set_can_focus(False)
        if pinned:
            button.get_style_context().add_class('pinned')
        button.connect('clicked', self.toggle_pin, row)
        row.pin_button = button
        line.pack_end(button, False, False, 0)
        self.list.add(row)
        row.show_all()
        if self.list.get_selected_row() is None and self.matches(row):
            self.list.select_row(row)

    def toggle_pin(self, button, row):
        try:
            set_pin(row.data, not row.pinned)
        except OSError:
            self.status.set_text('Impossible de sauvegarder le favori.')
            return
        row.pinned = not row.pinned
        button.set_label('★' if row.pinned else '☆')
        button.set_tooltip_text('Désépingler' if row.pinned else 'Épingler pour conserver')
        style = button.get_style_context()
        (style.add_class if row.pinned else style.remove_class)('pinned')
        self.list.invalidate_sort()
        self.update_status()

    def load_batch(self):
        for _ in range(12):
            entry = next(self.entries, None)
            if entry is None:
                self.loading = False
                self.update_status()
                return False
            try:
                self.add(run(['cliphist', 'decode'], input=entry, timeout=2).stdout)
            except (OSError, subprocess.SubprocessError):
                continue
        self.update_status()
        return True

    def matches(self, row):
        return self.search.get_text().casefold() in row.search_text

    def filter_changed(self, *_):
        self.list.invalidate_filter()
        visible = [r for r in self.list.get_children() if self.matches(r)]
        self.list.select_row(visible[0] if visible else None)
        self.update_status()

    def update_status(self):
        rows = self.list.get_children()
        visible = sum(self.matches(r) for r in rows)
        pins = sum(r.pinned for r in rows)
        self.status.set_text(f'{visible} éléments · {pins} épinglés · Entrée : coller · Ctrl+P : épingler · Échap : fermer' + (' · Chargement…' if self.loading else ''))

    def activate(self, _, row):
        self.result = row.data
        self.window.destroy()

    def keypress(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.window.destroy()
            return True
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
            row = self.list.get_selected_row()
            if row and self.matches(row):
                self.activate(self.list, row)
            return True
        if event.keyval in (Gdk.KEY_p, Gdk.KEY_P) and event.state & Gdk.ModifierType.CONTROL_MASK:
            row = self.list.get_selected_row()
            if row:
                self.toggle_pin(row.pin_button, row)
            return True
        if event.keyval in (Gdk.KEY_Down, Gdk.KEY_Up):
            rows = [r for r in self.list.get_children() if self.matches(r)]
            current = self.list.get_selected_row()
            index = rows.index(current) if current in rows else -1
            if rows:
                row = rows[max(0, min(len(rows)-1, index + (1 if event.keyval == Gdk.KEY_Down else -1)))]
                self.list.select_row(row)
                row.grab_focus()
            return True
        return False


def choose(entries, pins):
    picker = Picker(entries, pins)
    Gtk.main()
    if picker.loading:
        GLib.source_remove(picker.source)
    return picker.result
