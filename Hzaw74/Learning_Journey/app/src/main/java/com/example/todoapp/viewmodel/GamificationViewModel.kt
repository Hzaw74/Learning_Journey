package com.example.todoapp.viewmodel

import androidx.lifecycle.ViewModel
import com.example.todoapp.data.UserStatsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class GamificationViewModel @Inject constructor(
    private val userStatsRepository: UserStatsRepository
) : ViewModel() {
    val xp = userStatsRepository.xp
    val level = userStatsRepository.level

    fun toggleEatTheFrog() {
        userStatsRepository.toggleEatTheFrogMode()
    }
}
