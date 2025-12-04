package com.example.todoapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.todoapp.data.EnergyLevel
import com.example.todoapp.data.Priority
import com.example.todoapp.data.TodoItem
import com.example.todoapp.data.TodoRepository
import com.example.todoapp.data.UserStatsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class TodoViewModel @Inject constructor(
    private val repository: TodoRepository,
    private val userStatsRepository: UserStatsRepository
) : ViewModel() {

    // Using a simple list for now, can be optimized with Paging if needed
    val allTodos = repository.allTodos
    val isEatTheFrogMode = userStatsRepository.isEatTheFrogMode

    private val _uiState = MutableStateFlow(TodoUiState())
    val uiState: StateFlow<TodoUiState> = _uiState.asStateFlow()

    fun addTodo(
        title: String,
        description: String,
        priority: Priority,
        energyLevel: EnergyLevel,
        deadline: Long?,
        isUrgent: Boolean,
        isImportant: Boolean
    ) {
        viewModelScope.launch {
            repository.insert(
                TodoItem(
                    title = title,
                    description = description,
                    priority = priority,
                    energyLevel = energyLevel,
                    deadline = deadline,
                    isUrgent = isUrgent,
                    isImportant = isImportant
                )
            )
        }
    }

    fun updateTodo(todo: TodoItem) {
        viewModelScope.launch {
            repository.update(todo)
        }
    }

    fun deleteTodo(todo: TodoItem) {
        viewModelScope.launch {
            repository.delete(todo)
        }
    }

    fun onTodoCheckedChange(todo: TodoItem, isChecked: Boolean) {
        viewModelScope.launch {
            repository.update(todo.copy(isCompleted = isChecked))
            if (isChecked) {
                userStatsRepository.addXp(10) // 10 XP per task
            }
        }
    }
}

data class TodoUiState(
    val isLoading: Boolean = false,
    val userMessage: String? = null
)
