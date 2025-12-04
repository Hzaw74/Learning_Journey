package com.example.todoapp.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.todoapp.ui.navigation.Screen

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val items = listOf(
        Screen.TodoList,
        Screen.Calendar,
        Screen.FocusTimer,
        Screen.Matrix,
        Screen.Gamification
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                items.forEach { screen ->
                    NavigationBarItem(
                        icon = {
                            // Using standard icons for now, can be customized later
                            val iconVector = when(screen) {
                                Screen.TodoList -> Icons.Default.List
                                Screen.Calendar -> Icons.Default.DateRange
                                // Add others as needed, using placeholders for now
                                else -> Icons.Default.Person 
                            }
                            Icon(iconVector, contentDescription = screen.title)
                        },
                        label = { Text(screen.title) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(navController, startDestination = Screen.TodoList.route, Modifier.padding(innerPadding)) {
            composable(Screen.TodoList.route) { 
                com.example.todoapp.ui.todo.TodoListScreen(
                    onAddTodoClick = { navController.navigate(Screen.AddEditTodo.route) },
                    onTodoClick = { /* TODO: Navigate to edit */ }
                ) 
            }
            composable(Screen.Calendar.route) { 
                com.example.todoapp.ui.calendar.CalendarScreen() 
            }
            composable(Screen.FocusTimer.route) { 
                com.example.todoapp.ui.timer.FocusTimerScreen() 
            }
            composable(Screen.Matrix.route) { 
                com.example.todoapp.ui.matrix.MatrixScreen() 
            }
            composable(Screen.Gamification.route) { 
                com.example.todoapp.ui.gamification.GamificationScreen() 
            }
            composable(Screen.AddEditTodo.route) {
                com.example.todoapp.ui.todo.AddEditTodoScreen(
                    onNavigateUp = { navController.navigateUp() }
                )
            }
        }
    }
}
