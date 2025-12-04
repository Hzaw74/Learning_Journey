package com.example.todoapp.data

import android.content.Context
import android.content.SharedPreferences
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class UserStatsRepository @Inject constructor(
    @ApplicationContext context: Context
) {
    private val prefs: SharedPreferences = context.getSharedPreferences("user_stats", Context.MODE_PRIVATE)
    
    private val _xp = MutableStateFlow(prefs.getInt("xp", 0))
    val xp: StateFlow<Int> = _xp.asStateFlow()

    private val _level = MutableStateFlow(prefs.getInt("level", 1))
    val level: StateFlow<Int> = _level.asStateFlow()

    private val _isEatTheFrogMode = MutableStateFlow(prefs.getBoolean("eat_frog", false))
    val isEatTheFrogMode: StateFlow<Boolean> = _isEatTheFrogMode.asStateFlow()

    fun toggleEatTheFrogMode() {
        val newValue = !_isEatTheFrogMode.value
        _isEatTheFrogMode.value = newValue
        prefs.edit().putBoolean("eat_frog", newValue).apply()
    }

    fun addXp(amount: Int) {
        val newXp = _xp.value + amount
        _xp.value = newXp
        prefs.edit().putInt("xp", newXp).apply()
        checkLevelUp()
    }

    private fun checkLevelUp() {
        val currentLevel = _level.value
        val requiredXp = currentLevel * 100
        if (_xp.value >= requiredXp) {
            val newLevel = currentLevel + 1
            _level.value = newLevel
            prefs.edit().putInt("level", newLevel).apply()
        }
    }
}
