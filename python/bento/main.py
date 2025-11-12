import gi
import os

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, GObject

# Get the path to the UI file relative to the script
UI_FILE = os.path.join(os.path.dirname(__file__), 'bento.ui')

# Custom GObject class to hold task data (description and completion status)
class Task(GObject.Object):
    def __init__(self, description, is_completed=False):
        super().__init__()
        self._description = description
        self._is_completed = is_completed

    @GObject.Property
    def description(self):
        return self._description

    @GObject.Property
    def is_completed(self):
        return self._is_completed

    @is_completed.setter
    def is_completed(self, value):
        self._is_completed = value

@Gtk.Template(filename=UI_FILE)
class BentoWindow(Adw.ApplicationWindow):
    __gtype_name__ = "BentoWindow"

    # Stopwatch UI elements
    stopwatch_label = Gtk.Template.Child()
    stopwatch_toggle_button = Gtk.Template.Child()
    stopwatch_reset_button = Gtk.Template.Child()
    
    # Timer UI elements
    timer_spin_button = Gtk.Template.Child()
    timer_label = Gtk.Template.Child()
    timer_toggle_button = Gtk.Template.Child()
    timer_reset_button = Gtk.Template.Child()
    
    # Common UI elements
    mode_stack = Gtk.Template.Child()
    mode_switcher = Gtk.Template.Child()
    new_task_entry = Gtk.Template.Child()
    add_task_button = Gtk.Template.Child()
    todo_list_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set the Gtk.SpinButton properties here, not in the .ui file
        self.timer_spin_button.set_range(0, 3600)
        self.timer_spin_button.set_value(1500)
        
        # Connect signals for both timers
        self.stopwatch_toggle_button.connect('clicked', self.on_stopwatch_toggle_clicked)
        self.stopwatch_reset_button.connect('clicked', self.on_stopwatch_reset_clicked)
        self.timer_toggle_button.connect('clicked', self.on_timer_toggle_clicked)
        self.timer_reset_button.connect('clicked', self.on_timer_reset_clicked)
        
        # Connect signals for to-do list
        self.add_task_button.connect('clicked', self.on_add_task_clicked)
        self.new_task_entry.connect('activate', self.on_add_task_clicked)
        
        # Initial state for the stopwatch
        self.stopwatch_time_in_seconds = 0
        self.stopwatch_is_running = False
        self.stopwatch_source = None
        
        # Initial state for the timer
        self.initial_timer_seconds = self.timer_spin_button.get_value_as_int()
        self.timer_time_in_seconds = self.initial_timer_seconds
        self.timer_is_running = False
        self.timer_source = None
        self.update_timer_label()

        # To-Do List setup
        self.todo_list_store = Gio.ListStore.new(Task)
        self.todo_list_view.set_model(Gtk.SingleSelection.new(self.todo_list_store))

        factory = Gtk.SignalListItemFactory()
        factory.connect('setup', self.on_list_item_setup)
        factory.connect('bind', self.on_list_item_bind)
        self.todo_list_view.set_factory(factory)
        
        # Connect spin button value change
        self.timer_spin_button.connect('value-changed', self.on_spin_button_value_changed)
    
    # --- Stopwatch Logic ---
    def on_stopwatch_toggle_clicked(self, button):
        if self.stopwatch_is_running:
            self.stop_stopwatch()
            button.set_label("Start")
        else:
            self.start_stopwatch()
            button.set_label("Pause")
        self.stopwatch_is_running = not self.stopwatch_is_running

    def on_stopwatch_reset_clicked(self, button):
        self.stop_stopwatch()
        self.stopwatch_time_in_seconds = 0
        self.update_stopwatch_label()
        self.stopwatch_toggle_button.set_label("Start")
        self.stopwatch_is_running = False

    def start_stopwatch(self):
        self.stopwatch_source = GLib.timeout_add_seconds(1, self.on_stopwatch_tick)
        
    def stop_stopwatch(self):
        if self.stopwatch_source:
            GLib.source_remove(self.stopwatch_source)
            self.stopwatch_source = None

    def on_stopwatch_tick(self):
        self.stopwatch_time_in_seconds += 1
        self.update_stopwatch_label()
        return GLib.SOURCE_CONTINUE

    def update_stopwatch_label(self):
        hours = self.stopwatch_time_in_seconds // 3600
        minutes = (self.stopwatch_time_in_seconds % 3600) // 60
        seconds = self.stopwatch_time_in_seconds % 60
        self.stopwatch_label.set_label(f"{hours:02}:{minutes:02}:{seconds:02}")
    
    # --- Timer Logic ---
    def on_timer_toggle_clicked(self, button):
        if self.timer_is_running:
            self.stop_timer()
            button.set_label("Start")
        else:
            self.start_timer()
            button.set_label("Pause")
        self.timer_is_running = not self.timer_is_running

    def on_timer_reset_clicked(self, button):
        self.stop_timer()
        self.timer_time_in_seconds = self.initial_timer_seconds
        self.update_timer_label()
        self.timer_toggle_button.set_label("Start")
        self.timer_is_running = False

    def start_timer(self):
        self.timer_source = GLib.timeout_add_seconds(1, self.on_timer_tick)
        
    def stop_timer(self):
        if self.timer_source:
            GLib.source_remove(self.timer_source)
            self.timer_source = None

    def on_timer_tick(self):
        self.timer_time_in_seconds -= 1
        if self.timer_time_in_seconds < 0:
            self.stop_timer()
            self.timer_label.set_label("Time's up!")
            self.timer_toggle_button.set_label("Start")
            self.timer_is_running = False
            return GLib.SOURCE_REMOVE
        
        self.update_timer_label()
        return GLib.SOURCE_CONTINUE

    def update_timer_label(self):
        minutes = self.timer_time_in_seconds // 60
        seconds = self.timer_time_in_seconds % 60
        self.timer_label.set_label(f"{minutes:02}:{seconds:02}")
        
    def on_spin_button_value_changed(self, button):
        self.initial_timer_seconds = button.get_value_as_int()
        self.on_timer_reset_clicked(None)

    # --- To-Do List Logic ---
    def on_add_task_clicked(self, button):
        task_text = self.new_task_entry.get_text().strip()
        if task_text:
            new_task = Task(description=task_text)
            self.todo_list_store.append(new_task)
            self.new_task_entry.set_text("")
    
    def on_list_item_setup(self, factory, list_item):
        check_button = Gtk.CheckButton()
        check_button.connect("toggled", self.on_task_toggled, list_item)
        list_item.set_child(check_button)
        
    def on_list_item_bind(self, factory, list_item):
        check_button = list_item.get_child()
        task = list_item.get_item()
        check_button.set_label(task.description)
        check_button.set_active(task.is_completed)
        
    def on_task_toggled(self, check_button, list_item):
        task = list_item.get_item()
        task.is_completed = check_button.get_active()

class BentoApplication(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='com.example.bento', **kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = BentoWindow(application=app)
        self.win.present()

if __name__ == '__main__':
    app = BentoApplication()
    app.run(None)