package com.example.todoapp.data

import androidx.room.TypeConverter

class Converters {
    @TypeConverter
    fun fromPriority(priority: Priority): String {
        return priority.name
    }

    @TypeConverter
    fun toPriority(value: String): Priority {
        return Priority.valueOf(value)
    }

    @TypeConverter
    fun fromEnergyLevel(level: EnergyLevel): String {
        return level.name
    }

    @TypeConverter
    fun toEnergyLevel(value: String): EnergyLevel {
        return EnergyLevel.valueOf(value)
    }
}
