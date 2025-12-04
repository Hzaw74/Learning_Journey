package com.example.todoapp.ui.todo

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.todoapp.data.EnergyLevel
import com.example.todoapp.data.Priority
import com.example.todoapp.viewmodel.TodoViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AddEditTodoScreen(
    onNavigateUp: () -> Unit,
    viewModel: TodoViewModel = hiltViewModel()
) {
    var title by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var priority by remember { mutableStateOf(Priority.MEDIUM) }
    var energyLevel by remember { mutableStateOf(EnergyLevel.MEDIUM) }
    var isUrgent by remember { mutableStateOf(false) }
    var isImportant by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Add Task") },
                navigationIcon = {
                    IconButton(onClick = onNavigateUp) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("Title") },
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = description,
                onValueChange = { description = it },
                label = { Text("Description") },
                modifier = Modifier.fillMaxWidth(),
                minLines = 3
            )

            // Priority Selector
            Text("Priority", style = MaterialTheme.typography.titleSmall)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Priority.values().forEach { p ->
                    FilterChip(
                        selected = priority == p,
                        onClick = { priority = p },
                        label = { Text(p.name) }
                    )
                }
            }

            // Energy Level Selector
            Text("Energy Level", style = MaterialTheme.typography.titleSmall)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                EnergyLevel.values().forEach { e ->
                    FilterChip(
                        selected = energyLevel == e,
                        onClick = { energyLevel = e },
                        label = { Text(e.name) }
                    )
                }
            }

            // Eisenhower Matrix Toggles
            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                Checkbox(checked = isUrgent, onCheckedChange = { isUrgent = it })
                Text("Urgent")
            }
            Row(verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                Checkbox(checked = isImportant, onCheckedChange = { isImportant = it })
                Text("Important")
            }

            Button(
                onClick = {
                    viewModel.addTodo(
                        title = title,
                        description = description,
                        priority = priority,
                        energyLevel = energyLevel,
                        deadline = null, // TODO: Add DatePicker
                        isUrgent = isUrgent,
                        isImportant = isImportant
                    )
                    onNavigateUp()
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = title.isNotBlank()
            ) {
                Text("Save Task")
            }
        }
    }
}
