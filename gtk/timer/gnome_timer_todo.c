#include <gtk/gtk.h>
#include <time.h>

// Timer variables
static guint timer_seconds = 0;
static gboolean timer_running = FALSE;
static GtkLabel *timer_label;

// Stopwatch variables
static guint stopwatch_seconds = 0;
static gboolean stopwatch_running = FALSE;
static GtkLabel *stopwatch_label;

// To-do list variables
static GtkListBox *todo_list;
static GtkEntry *todo_entry;

// Timer update function
static gboolean update_timer(gpointer user_data) {
    if (timer_running && timer_seconds > 0) {
        timer_seconds--;
        gchar *text = g_strdup_printf("Timer: %02d:%02d", timer_seconds / 60, timer_seconds % 60);
        gtk_label_set_text(timer_label, text);
        g_free(text);
        if (timer_seconds == 0) {
            timer_running = FALSE;
        }
    }
    return TRUE;
}

// Stopwatch update function
static gboolean update_stopwatch(gpointer user_data) {
    if (stopwatch_running) {
        stopwatch_seconds++;
        gchar *text = g_strdup_printf("Stopwatch: %02d:%02d", stopwatch_seconds / 60, stopwatch_seconds % 60);
        gtk_label_set_text(stopwatch_label, text);
        g_free(text);
    }
    return TRUE;
}

// Timer start
static void on_start_timer(GtkButton *button, gpointer user_data) {
    timer_seconds = 60; // 1 minute timer for example
    timer_running = TRUE;
}

// Stopwatch start/stop
static void on_toggle_stopwatch(GtkButton *button, gpointer user_data) {
    stopwatch_running = !stopwatch_running;
}

// Add to-do item
static void on_add_todo(GtkButton *button, gpointer user_data) {
    const gchar *text = gtk_editable_get_text(GTK_EDITABLE(todo_entry));
    if (g_strcmp0(text, "") != 0) {
        GtkWidget *row = gtk_label_new(text);
        gtk_list_box_append(todo_list, row);
        gtk_editable_set_text(GTK_EDITABLE(todo_entry), "");
    }
}

static void activate(GtkApplication *app, gpointer user_data) {
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Timer, Stopwatch, To-do List");
    gtk_window_set_default_size(GTK_WINDOW(window), 300, 400);

    GtkWidget *grid = gtk_grid_new();
    gtk_widget_set_margin_top(grid, 10);
    gtk_widget_set_margin_bottom(grid, 10);
    gtk_widget_set_margin_start(grid, 10);
    gtk_widget_set_margin_end(grid, 10);
    gtk_grid_set_row_spacing(GTK_GRID(grid), 10);
    gtk_grid_set_column_spacing(GTK_GRID(grid), 10);
    gtk_window_set_child(GTK_WINDOW(window), grid);

    // Timer UI
    timer_label = GTK_LABEL(gtk_label_new("Timer: 00:00"));
    GtkWidget *start_timer_btn = gtk_button_new_with_label("Start Timer");
    g_signal_connect(start_timer_btn, "clicked", G_CALLBACK(on_start_timer), NULL);
    gtk_grid_attach(GTK_GRID(grid), GTK_WIDGET(timer_label), 0, 0, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), start_timer_btn, 1, 0, 1, 1);

    // Stopwatch UI
    stopwatch_label = GTK_LABEL(gtk_label_new("Stopwatch: 00:00"));
    GtkWidget *toggle_stopwatch_btn = gtk_button_new_with_label("Start/Stop Stopwatch");
    g_signal_connect(toggle_stopwatch_btn, "clicked", G_CALLBACK(on_toggle_stopwatch), NULL);
    gtk_grid_attach(GTK_GRID(grid), GTK_WIDGET(stopwatch_label), 0, 1, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), toggle_stopwatch_btn, 1, 1, 1, 1);

    // To-do list UI
    todo_entry = GTK_ENTRY(gtk_entry_new());
    GtkWidget *add_todo_btn = gtk_button_new_with_label("Add To-do");
    g_signal_connect(add_todo_btn, "clicked", G_CALLBACK(on_add_todo), NULL);
    todo_list = GTK_LIST_BOX(gtk_list_box_new());
    gtk_widget_set_vexpand(GTK_WIDGET(todo_list), TRUE);
    gtk_grid_attach(GTK_GRID(grid), GTK_WIDGET(todo_entry), 0, 2, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), add_todo_btn, 1, 2, 1, 1);
    gtk_grid_attach(GTK_GRID(grid), GTK_WIDGET(todo_list), 0, 3, 2, 1);

    // Timers for updating UI
    g_timeout_add_seconds(1, update_timer, NULL);
    g_timeout_add_seconds(1, update_stopwatch, NULL);

    gtk_widget_show(window);
}

int main(int argc, char **argv) {
    GtkApplication *app = gtk_application_new("org.example.TimerTodo", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}
