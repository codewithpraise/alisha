package com.friendos.alishabubbzieee.core.proactive

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import java.util.Calendar

/**
 * Autonomous Proactive Messaging Worker.
 * Allows Alisha to text and send messages on her own without user prompting.
 * Runs periodically via Android WorkManager.
 * Evaluates time of day and companion tone before sending rich notification.
 */
class ProactiveMessagingWorker(
    appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)

        // Time-of-day contextual autonomous messages in authentic Alisha voice
        val proactiveMessage = when (hour) {
            in 0..4 -> "u still awake? ... go to sleep latw 😭"
            in 8..11 -> "morning. hope your day goes alright"
            in 14..17 -> "busy with things? take a break"
            in 22..23 -> "what are you up to tonight"
            else -> "thinking about where i put my phone lol"
        }

        val notificationManager = ProactiveNotificationManager(applicationContext)
        notificationManager.showProactiveMessage(proactiveMessage)

        return Result.success()
    }
}
