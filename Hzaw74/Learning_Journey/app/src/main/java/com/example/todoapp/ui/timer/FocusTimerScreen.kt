package com.example.todoapp.ui.timer

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.todoapp.viewmodel.AmbientSound
import com.example.todoapp.viewmodel.TimerViewModel

@Composable
fun FocusTimerScreen(
    viewModel: TimerViewModel = hiltViewModel()
) {
    val state by viewModel.timerState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = formatTime(state.timeLeft),
            style = MaterialTheme.typography.displayLarge.copy(fontSize = 80.sp),
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        Row(
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Button(onClick = { viewModel.toggleTimer() }) {
                Icon(
                    if (state.isRunning) Icons.Default.PlayArrow else Icons.Default.PlayArrow, // TODO: Add Pause icon
                    contentDescription = if (state.isRunning) "Pause" else "Start"
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(if (state.isRunning) "Pause" else "Start")
            }

            OutlinedButton(onClick = { viewModel.resetTimer() }) {
                Icon(Icons.Default.Refresh, contentDescription = "Reset")
            }
        }

        Spacer(modifier = Modifier.height(48.dp))

        Text("Ambient Sounds", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(16.dp))
        
        // Sound Chips
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            AmbientSound.values().forEach { sound ->
                FilterChip(
                    selected = state.selectedSound == sound,
                    onClick = { 
                        if (state.selectedSound == sound) viewModel.setAmbientSound(null)
                        else viewModel.setAmbientSound(sound)
                    },
                    label = { Text(sound.displayName) }
                )
            }
        }
    }
}

fun formatTime(seconds: Int): String {
    val minutes = seconds / 60
    val remainingSeconds = seconds % 60
    return "%02d:%02d".format(minutes, remainingSeconds)
}
