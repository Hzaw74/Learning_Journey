package com.example.productivity.ui.timer

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay

class TimerViewModel : ViewModel() {
    var timeLeftSeconds by mutableStateOf(0L)
        private set
    var isRunning by mutableStateOf(false)
        private set
    var initialDurationSeconds by mutableStateOf(0L)
        private set

    suspend fun runTimer() {
        while (isRunning && timeLeftSeconds > 0) {
            delay(1000)
            if (isRunning) { // check again
                timeLeftSeconds--
            }
        }
        if (timeLeftSeconds == 0L) {
            isRunning = false
        }
    }

    fun start(seconds: Long) {
        if (seconds > 0) {
            initialDurationSeconds = seconds
            timeLeftSeconds = seconds
            isRunning = true
        }
    }
    
    fun resume() {
        if (timeLeftSeconds > 0) {
            isRunning = true
        }
    }

    fun pause() {
        isRunning = false
    }

    fun reset() {
        isRunning = false
        timeLeftSeconds = initialDurationSeconds // or 0? usually reset to initial
        // if initial was 0, just 0
    }
    
    fun setDuration(seconds: Long) {
        initialDurationSeconds = seconds
        timeLeftSeconds = seconds
        isRunning = false
    }
}

@Composable
fun TimerScreen(viewModel: TimerViewModel = viewModel()) {
    // Input state
    var minutesInput by remember { mutableStateOf("0") }
    var secondsInput by remember { mutableStateOf("0") }

    LaunchedEffect(viewModel.isRunning) {
        if (viewModel.isRunning) {
            viewModel.runTimer()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        if (!viewModel.isRunning && viewModel.timeLeftSeconds == 0L && viewModel.initialDurationSeconds == 0L) {
            // Setup Mode
            Text("Set Timer", style = MaterialTheme.typography.headlineLarge)
            Spacer(modifier = Modifier.height(32.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                OutlinedTextField(
                    value = minutesInput,
                    onValueChange = { if (it.all { char -> char.isDigit() }) minutesInput = it },
                    label = { Text("Min") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
                Spacer(modifier = Modifier.width(16.dp))
                OutlinedTextField(
                    value = secondsInput,
                    onValueChange = { if (it.all { char -> char.isDigit() }) secondsInput = it },
                    label = { Text("Sec") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(modifier = Modifier.height(32.dp))
            Button(
                onClick = {
                    val min = minutesInput.toLongOrNull() ?: 0
                    val sec = secondsInput.toLongOrNull() ?: 0
                    val totalSeconds = min * 60 + sec
                    viewModel.start(totalSeconds)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Start")
            }
        } else {
            // Running/Paused Mode
            val minutes = viewModel.timeLeftSeconds / 60
            val seconds = viewModel.timeLeftSeconds % 60
            val timeString = String.format("%02d:%02d", minutes, seconds)

            Text(
                text = timeString,
                style = MaterialTheme.typography.displayLarge.copy(
                    fontSize = MaterialTheme.typography.displayLarge.fontSize * 2,
                    fontWeight = FontWeight.Bold
                ),
                color = if (viewModel.timeLeftSeconds < 10 && viewModel.isRunning) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onBackground
            )
            Spacer(modifier = Modifier.height(32.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                if (viewModel.isRunning) {
                    Button(onClick = { viewModel.pause() }) {
                        Text("Pause")
                    }
                } else {
                     Button(onClick = { viewModel.resume() }) {
                        Text("Resume")
                    }
                }
                
                OutlinedButton(onClick = { 
                    viewModel.reset()
                    // If we want to fully reset to input mode:
                    viewModel.setDuration(0)
                }) {
                    Text("Reset")
                }
            }
        }
    }
}
