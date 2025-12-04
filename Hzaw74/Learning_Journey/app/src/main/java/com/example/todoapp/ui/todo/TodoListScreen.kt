package com.example.todoapp.ui.todo

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.todoapp.data.TodoItem
import com.example.todoapp.viewmodel.TodoViewModel
import androidx.compose.runtime.*
import com.example.todoapp.data.EnergyLevel

@Composable
fun TodoListScreen(
    onAddTodoClick: () -> Unit,
    onTodoClick: (TodoItem) -> Unit,
    viewModel: TodoViewModel = hiltViewModel()
) {
    val todos by viewModel.allTodos.collectAsState(initial = emptyList())
    val isEatTheFrogMode by viewModel.isEatTheFrogMode.collectAsState(initial = false)
    var selectedEnergy by remember { mutableStateOf<EnergyLevel?>(null) }

    val filteredTodos = remember(todos, selectedEnergy) {
        if (selectedEnergy == null) todos
        else todos.filter { it.energyLevel == selectedEnergy }
    }
    
    // Eat the Frog Logic: Find highest priority task
    val frogTask = remember(todos) {
        todos.filter { !it.isCompleted }
             .maxByOrNull { it.priority.ordinal } // Assuming HIGH is last ordinal
    }

    Scaffold(
        floatingActionButton = {
            FloatingActionButton(onClick = onAddTodoClick) {
                Icon(Icons.Default.Add, contentDescription = "Add Todo")
            }
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
        ) {
            // Energy Filter Chips
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedEnergy == null,
                    onClick = { selectedEnergy = null },
                    label = { Text("All") }
                )
                EnergyLevel.values().forEach { level ->
                    FilterChip(
                        selected = selectedEnergy == level,
                        onClick = { selectedEnergy = if (selectedEnergy == level) null else level },
                        label = { Text(level.name) }
                    )
                }
            }

            items(filteredTodos) { todo ->
                val isEnabled = if (isEatTheFrogMode && !todo.isCompleted) {
                    todo.id == frogTask?.id
                } else {
                    true
                }
                
                TodoItemCard(
                    todo = todo,
                    isEnabled = isEnabled,
                    onCheckedChange = { isChecked ->
                        viewModel.onTodoCheckedChange(todo, isChecked)
                    },
                    onClick = { if (isEnabled) onTodoClick(todo) },
                    onDeleteClick = { viewModel.deleteTodo(todo) }
                )
            }
        }
    }
}

@Composable
fun TodoItemCard(
    todo: TodoItem,
    isEnabled: Boolean = true,
    onCheckedChange: (Boolean) -> Unit,
    onClick: () -> Unit,
    onDeleteClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = isEnabled, onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isEnabled) MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)
        )
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = todo.isCompleted,
                onCheckedChange = if (isEnabled) onCheckedChange else null,
                enabled = isEnabled
            )
            Spacer(modifier = Modifier.width(8.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = todo.title,
                    style = MaterialTheme.typography.titleMedium,
                    textDecoration = if (todo.isCompleted) TextDecoration.LineThrough else null
                )
                if (todo.description.isNotBlank()) {
                    Text(
                        text = todo.description,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            IconButton(onClick = onDeleteClick) {
                Icon(Icons.Default.Delete, contentDescription = "Delete", tint = MaterialTheme.colorScheme.error)
            }
        }
    }
}
