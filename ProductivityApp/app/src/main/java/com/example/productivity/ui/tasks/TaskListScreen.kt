package com.example.productivity.ui.tasks

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.Checkbox
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskListScreen(viewModel: TasksViewModel = viewModel()) {
    var newTaskText by remember { mutableStateOf("") }
    val tasks = viewModel.tasks

    Scaffold(
        topBar = {
             Row(
                 modifier = Modifier
                     .fillMaxWidth()
                     .padding(16.dp),
                 verticalAlignment = Alignment.CenterVertically
             ) {
                 OutlinedTextField(
                     value = newTaskText,
                     onValueChange = { newTaskText = it },
                     label = { Text("New Task") },
                     modifier = Modifier.weight(1f),
                     singleLine = true
                 )
                 IconButton(
                     onClick = {
                         viewModel.addTask(newTaskText)
                         newTaskText = ""
                     },
                     modifier = Modifier.padding(start = 8.dp)
                 ) {
                     Icon(Icons.Default.Add, contentDescription = "Add Task")
                 }
             }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp)
        ) {
            items(tasks, key = { it.id }) { task ->
                TaskItem(
                    task = task,
                    onToggle = { viewModel.toggleTask(task.id) },
                    onDelete = { viewModel.removeTask(task.id) }
                )
            }
        }
    }
}

@Composable
fun TaskItem(
    task: Task,
    onToggle: () -> Unit,
    onDelete: () -> Unit
) {
    ListItem(
        headlineContent = {
            Text(
                text = task.text,
                textDecoration = if (task.isCompleted) TextDecoration.LineThrough else null
            )
        },
        leadingContent = {
            Checkbox(
                checked = task.isCompleted,
                onCheckedChange = { onToggle() }
            )
        },
        trailingContent = {
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "Delete Task")
            }
        },
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .clickable { onToggle() }
    )
}
