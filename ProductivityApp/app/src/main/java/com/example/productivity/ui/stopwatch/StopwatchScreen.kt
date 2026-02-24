package com.example.productivity.ui.stopwatch

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay

class StopwatchViewModel : ViewModel() {
    var timeMillis by mutableStateOf(0L)
        private set
    var isRunning by mutableStateOf(false)
        private set

    suspend fun runStopwatch() {
        val startTime = System.currentTimeMillis() - timeMillis
        while (isRunning) {
            // Update time
            timeMillis = System.currentTimeMillis() - startTime
            delay(10) // 100fps roughly
        }
    }

    fun start() {
        isRunning = true
    }

    fun pause() {
        isRunning = false
    }

    fun reset() {
        isRunning = false
        timeMillis = 0L
    }
}

@Composable
fun StopwatchScreen(viewModel: StopwatchViewModel = viewModel()) {
    LaunchedEffect(viewModel.isRunning) {
        if (viewModel.isRunning) {
            viewModel.runStopwatch()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        val totalSeconds = viewModel.timeMillis / 1000
        val minutes = totalSeconds / 60
        val seconds = totalSeconds % 60
        val millis = (viewModel.timeMillis % 1000) / 10 // Show 2 digits
        
        val timeString = String.format("%02d:%02d.%02d", minutes, seconds, millis)

        Text(
            text = timeString,
            style = MaterialTheme.typography.displayLarge.copy(
                fontSize = MaterialTheme.typography.displayLarge.fontSize * 1.5,
                fontWeight = FontWeight.Bold,
                fontFeatureSettings = "tnum" // Tabular numbers for non-jittery text
            ),
            color = MaterialTheme.colorScheme.primary
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            if (viewModel.isRunning) {
                Button(onClick = { viewModel.pause() }, modifier = Modifier.weight(1f)) {
                    Text("Pause")
                }
            } else {
                Button(onClick = { viewModel.start() }, modifier = Modifier.weight(1f)) {
                    Text("Start")
                }
            }
            
            OutlinedButton(onClick = { viewModel.reset() }, modifier = Modifier.weight(1f)) {
                Text("Reset")
            }
        }
    }
}
