package com.example.productivity.ui.tasks

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import java.util.UUID

data class Task(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val isCompleted: Boolean = false
)

class TasksViewModel : ViewModel() {
    private val _tasks = mutableStateListOf<Task>()
    val tasks: List<Task> get() = _tasks

    // Initialize with some dummy data
    init {
        _tasks.add(Task(text = "Welcome to your productivity app!"))
        _tasks.add(Task(text = "Add a new task below."))
        _tasks.add(Task(text = "Tick me off when done.", isCompleted = true))
    }

    fun addTask(text: String) {
        if (text.isNotBlank()) {
            _tasks.add(0, Task(text = text))
        }
    }

    fun toggleTask(taskId: String) {
        val index = _tasks.indexOfFirst { it.id == taskId }
        if (index != -1) {
            val task = _tasks[index]
            _tasks[index] = task.copy(isCompleted = !task.isCompleted)
        }
    }

    fun removeTask(taskId: String) {
        _tasks.removeAll { it.id == taskId }
    }
}
