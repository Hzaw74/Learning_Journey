package com.example.todoapp.logic

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NotificationManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    fun scheduleNotification(todoId: Int, title: String, deadline: Long) {
        // TODO: Implement AlarmManager or WorkManager logic here
        // 1. Create Intent for BroadcastReceiver
        // 2. Get AlarmManager system service
        // 3. Schedule alarm
    }

    fun cancelNotification(todoId: Int) {
        // TODO: Cancel scheduled alarm
    }
}
