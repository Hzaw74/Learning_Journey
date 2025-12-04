package com.example.todoapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class TimerViewModel @Inject constructor() : ViewModel() {

    private val _timerState = MutableStateFlow(TimerState())
    val timerState: StateFlow<TimerState> = _timerState.asStateFlow()

    private var timerJob: Job? = null

    fun toggleTimer() {
        if (_timerState.value.isRunning) {
            pauseTimer()
        } else {
            startTimer()
        }
    }

    private fun startTimer() {
        _timerState.value = _timerState.value.copy(isRunning = true)
        timerJob = viewModelScope.launch {
            while (_timerState.value.timeLeft > 0) {
                delay(1000L)
                _timerState.value = _timerState.value.copy(timeLeft = _timerState.value.timeLeft - 1)
            }
            _timerState.value = _timerState.value.copy(isRunning = false, timeLeft = 25 * 60) // Reset to 25 min
            // TODO: Trigger notification or sound
        }
    }

    private fun pauseTimer() {
        _timerState.value = _timerState.value.copy(isRunning = false)
        timerJob?.cancel()
    }

    fun resetTimer() {
        pauseTimer()
        _timerState.value = _timerState.value.copy(timeLeft = 25 * 60)
    }

    fun setAmbientSound(sound: AmbientSound?) {
        _timerState.value = _timerState.value.copy(selectedSound = sound)
        // TODO: Implement actual MediaPlayer logic here
    }
}

data class TimerState(
    val isRunning: Boolean = false,
    val timeLeft: Int = 25 * 60, // 25 minutes in seconds
    val selectedSound: AmbientSound? = null
)

enum class AmbientSound(val displayName: String) {
    WHITE_NOISE("White Noise"),
    RAIN("Rain"),
    LO_FI("Lo-Fi Beats"),
    FOREST("Forest")
}
