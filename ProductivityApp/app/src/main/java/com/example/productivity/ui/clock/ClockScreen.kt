package com.example.productivity.ui.clock

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
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
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Composable
fun ClockScreen() {
    var currentTime by remember { mutableStateOf(LocalDateTime.now()) }

    LaunchedEffect(Unit) {
        while (true) {
            currentTime = LocalDateTime.now()
            delay(1000)
        }
    }

    val timeFormatter = DateTimeFormatter.ofPattern("HH:mm")
    val secondsFormatter = DateTimeFormatter.ofPattern("ss")
    val dateFormatter = DateTimeFormatter.ofPattern("EEEE, MMMM d")

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = currentTime.format(dateFormatter),
                style = MaterialTheme.typography.headlineMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = currentTime.format(timeFormatter),
                style = MaterialTheme.typography.displayLarge.copy(
                    fontSize = MaterialTheme.typography.displayLarge.fontSize * 2,
                    fontWeight = FontWeight.Bold
                ),
                color = MaterialTheme.colorScheme.onBackground
            )
            Text(
                text = currentTime.format(secondsFormatter),
                style = MaterialTheme.typography.displayMedium,
                color = MaterialTheme.colorScheme.secondary
            )
        }
    }
}
