package com.example.todoapp.ui.gamification

import androidx.compose.foundation.layout.*
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.example.todoapp.viewmodel.GamificationViewModel

@Composable
fun GamificationScreen(
    viewModel: GamificationViewModel = hiltViewModel()
) {
    val xp by viewModel.xp.collectAsState()
    val level by viewModel.level.collectAsState()
    val nextLevelXp = level * 100
    val progress = xp.toFloat() / nextLevelXp.toFloat()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Level $level", style = MaterialTheme.typography.displayLarge)
        Spacer(modifier = Modifier.height(16.dp))
        LinearProgressIndicator(
            progress = progress,
            modifier = Modifier.fillMaxWidth().height(16.dp)
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text("$xp / $nextLevelXp XP", style = MaterialTheme.typography.bodyLarge)
        
        Spacer(modifier = Modifier.height(32.dp))
        Text("Keep completing tasks to level up!", style = MaterialTheme.typography.titleMedium)
        
        Spacer(modifier = Modifier.height(32.dp))
        Button(onClick = { viewModel.toggleEatTheFrog() }) {
            Text("Toggle 'Eat the Frog' Mode")
        }
    }
}
