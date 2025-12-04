package com.example.todoapp.data

import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class TodoRepository @Inject constructor(private val todoDao: TodoDao) {
    val allTodos: Flow<List<TodoItem>> = todoDao.getAllTodos()

    suspend fun insert(todo: TodoItem) {
        todoDao.insertTodo(todo)
    }

    suspend fun update(todo: TodoItem) {
        todoDao.updateTodo(todo)
    }

    suspend fun delete(todo: TodoItem) {
        todoDao.deleteTodo(todo)
    }
    
    suspend fun getTodoById(id: Int): TodoItem? {
        return todoDao.getTodoById(id)
    }
}
