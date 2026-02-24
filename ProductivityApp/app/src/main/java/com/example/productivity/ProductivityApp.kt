package com.example.productivity

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.example.productivity.ui.clock.ClockScreen
import com.example.productivity.ui.tasks.TaskListScreen
import com.example.productivity.ui.timer.TimerScreen
import com.example.productivity.ui.stopwatch.StopwatchScreen
// import com.example.productivity.R // Will need to create drawable resources or use Icons.Default

sealed class Screen(val route: String, val label: String, val iconName: String) {
    object Clock : Screen("clock", "Clock", "ic_clock") 
    object Tasks : Screen("tasks", "Tasks", "ic_task")
    object Timer : Screen("timer", "Timer", "ic_timer")
    object Stopwatch : Screen("stopwatch", "Stopwatch", "ic_stopwatch")
}

@Composable
fun ProductivityApp() {
    val navController = rememberNavController()
    
    val items = listOf(
        Screen.Clock,
        Screen.Tasks,
        Screen.Timer,
        Screen.Stopwatch,
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                items.forEach { screen ->
                    NavigationBarItem(
                        icon = { Text(screen.label.take(1)) }, // Temporary icon
                        label = { Text(screen.label) },
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
        NavHost(navController, startDestination = Screen.Clock.route, Modifier.padding(innerPadding)) {
            composable(Screen.Clock.route) { ClockScreen() }
            composable(Screen.Tasks.route) { TaskListScreen() }
            composable(Screen.Timer.route) { TimerScreen() }
            composable(Screen.Stopwatch.route) { StopwatchScreen() }
        }
    }
}
