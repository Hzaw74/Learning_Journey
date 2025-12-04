package com.example.todoapp.ui.matrix

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.todoapp.data.TodoItem
import com.example.todoapp.viewmodel.TodoViewModel

@Composable
fun MatrixScreen(
    viewModel: TodoViewModel = hiltViewModel()
) {
    val todos by viewModel.allTodos.collectAsState(initial = emptyList())

    Column(modifier = Modifier.fillMaxSize()) {
        Row(modifier = Modifier.weight(1f)) {
            Quadrant(
                title = "Do First (Urgent & Important)",
                todos = todos.filter { it.isUrgent && it.isImportant },
                color = Color(0xFFFFCDD2), // Light Red
                modifier = Modifier.weight(1f).fillMaxHeight()
            )
            Quadrant(
                title = "Schedule (Important, Not Urgent)",
                todos = todos.filter { !it.isUrgent && it.isImportant },
                color = Color(0xFFC8E6C9), // Light Green
                modifier = Modifier.weight(1f).fillMaxHeight()
            )
        }
        Row(modifier = Modifier.weight(1f)) {
            Quadrant(
                title = "Delegate (Urgent, Not Important)",
                todos = todos.filter { it.isUrgent && !it.isImportant },
                color = Color(0xFFFFF9C4), // Light Yellow
                modifier = Modifier.weight(1f).fillMaxHeight()
            )
            Quadrant(
                title = "Delete (Not Urgent, Not Important)",
                todos = todos.filter { !it.isUrgent && !it.isImportant },
                color = Color(0xFFE0E0E0), // Light Grey
                modifier = Modifier.weight(1f).fillMaxHeight()
            )
        }
    }
}

@Composable
fun Quadrant(
    title: String,
    todos: List<TodoItem>,
    color: Color,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .background(color)
            .padding(8.dp)
            .border(1.dp, Color.Black)
    ) {
        Text(text = title, style = MaterialTheme.typography.labelLarge, modifier = Modifier.padding(bottom = 8.dp))
        LazyColumn {
            items(todos) { todo ->
                Text(text = "• ${todo.title}", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
