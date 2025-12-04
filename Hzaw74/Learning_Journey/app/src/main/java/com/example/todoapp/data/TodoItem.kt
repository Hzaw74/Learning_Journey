package com.example.todoapp.data

import androidx.room.Entity
import androidx.room.PrimaryKey

enum class Priority {
    LOW, MEDIUM, HIGH
}

enum class EnergyLevel {
    LOW, MEDIUM, HIGH
}

@Entity(tableName = "todo_items")
data class TodoItem(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val title: String,
    val description: String = "",
    val isCompleted: Boolean = false,
    val deadline: Long? = null, // Timestamp
    val priority: Priority = Priority.MEDIUM,
    val energyLevel: EnergyLevel = EnergyLevel.MEDIUM, // Niche feature
    val isUrgent: Boolean = false, // Eisenhower Matrix
    val isImportant: Boolean = false // Eisenhower Matrix
)
