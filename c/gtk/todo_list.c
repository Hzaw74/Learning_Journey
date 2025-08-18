#include <gtk/gtk.h>

// Handler to remove a task when clicked
static void on_task_clicked(GtkWidget *widget, gpointer user_data) {
    gtk_list_box_remove(GTK_LIST_BOX(user_data), widget);
}

// Handler to add a new task
static void on_add_clicked(GtkButton *button, gpointer user_data) {
    GtkEntry *entry = GTK_ENTRY(g_object_get_data(G_OBJECT(button), "entry"));
    GtkListBox *list_box = GTK_LIST_BOX(user_data);

    const gchar *text = gtk_entry_get_text(entry);
    if (g_strcmp0(text, "") != 0) {
        GtkWidget *row = gtk_label_new(text);
        gtk_widget_set_halign(row, GTK_ALIGN_START);
        gtk_widget_set_margin_top(row, 4);
        gtk_widget_set_margin_bottom(row, 4);
        gtk_widget_set_margin_start(row, 10);
        gtk_widget_set_margin_end(row, 10);

        // Add click signal to remove item
        g_signal_connect(row, "button-press-event", G_CALLBACK(on_task_clicked), list_box);
        gtk_list_box_append(list_box, row);
        gtk_widget_show(row);

        gtk_entry_set_text(entry, ""); // clear input
    }
}

int main(int argc, char *argv[]) {
    gtk_init();

    GtkWidget *window = gtk_window_new();
    gtk_window_set_title(GTK_WINDOW(window), "Todo List");
    gtk_window_set_default_size(GTK_WINDOW(window), 300, 400);
    gtk_window_set_hide_on_close(GTK_WINDOW(window), FALSE);

    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    gtk_widget_set_margin_top(vbox, 10);
    gtk_widget_set_margin_bottom(vbox, 10);
    gtk_widget_set_margin_start(vbox, 10);
    gtk_widget_set_margin_end(vbox, 10);
    gtk_window_set_child(GTK_WINDOW(window), vbox);

    GtkWidget *entry = gtk_entry_new();
    gtk_box_append(GTK_BOX(vbox), entry);

    GtkWidget *button = gtk_button_new_with_label("Add Task");
    gtk_box_append(GTK_BOX(vbox), button);

    GtkWidget *scrolled = gtk_scrolled_window_new();
    gtk_widget_set_vexpand(scrolled, TRUE);
    gtk_box_append(GTK_BOX(vbox), scrolled);

    GtkWidget *list_box = gtk_list_box_new();
    gtk_scrolled_window_set_child(GTK_SCROLLED_WINDOW(scrolled), list_box);

    // Connect button
    g_object_set_data(G_OBJECT(button), "entry", entry);
    g_signal_connect(button, "clicked", G_CALLBACK(on_add_clicked), list_box);

    gtk_window_present(GTK_WINDOW(window));
    gtk_main();
    return 0;
}
