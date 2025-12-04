package com.example.todoapp.ui.navigation

sealed class Screen(val route: String, val title: String, val icon: String) {
    object TodoList : Screen("todo_list", "Tasks", "list")
    object Calendar : Screen("calendar", "Calendar", "calendar_today")
    object FocusTimer : Screen("focus_timer", "Focus", "timer")
    object Matrix : Screen("matrix", "Matrix", "grid_view")
    object Gamification : Screen("gamification", "Profile", "person")
    object AddEditTodo : Screen("add_edit_todo", "Add Task", "add")
}
