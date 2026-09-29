package com.friendos.alishabubbzieee.core.proactive

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.Person
import androidx.core.app.RemoteInput
import com.friendos.alishabubbzieee.ui.MainActivity

/**
 * Rich Audio & UI Notification Manager.
 * Delivers warm, intimate notifications when Alisha texts unprompted.
 * Features:
 * - High priority channel with gentle acoustic notification sound
 * - Android MessagingStyle for conversation depth
 * - Direct inline reply affordance
 */
class ProactiveNotificationManager(private val context: Context) {

    companion object {
        const val CHANNEL_ID = "alisha_companion_channel"
        const val CHANNEL_NAME = "alisha"
        const val NOTIFICATION_ID = 2026
        const val KEY_TEXT_REPLY = "key_text_reply"
    }

    init {
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val audioAttributes = AudioAttributes.Builder()
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .setUsage(AudioAttributes.USAGE_NOTIFICATION_COMMUNICATION_INSTANT)
                .build()

            val soundUri = Uri.parse("android.resource://${context.packageName}/raw/alisha_ping")

            val channel = NotificationChannel(
                CHANNEL_ID,
                CHANNEL_NAME,
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Warm personal messages from Alisha"
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 120, 80, 180)
                setSound(soundUri, audioAttributes)
            }

            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    fun showProactiveMessage(messageText: String) {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }

        val pendingIntent = PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val alishaPerson = Person.Builder()
            .setName("alisha")
            .setImportant(true)
            .build()

        val messagingStyle = NotificationCompat.MessagingStyle(alishaPerson)
            .setConversationTitle("alisha")
            .addMessage(messageText, System.currentTimeMillis(), alishaPerson)

        // Direct Reply Action
        val remoteInput = RemoteInput.Builder(KEY_TEXT_REPLY)
            .setLabel("say something…")
            .build()

        val replyPendingIntent = PendingIntent.getActivity(
            context,
            1,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
        )

        val replyAction = NotificationCompat.Action.Builder(
            android.R.drawable.ic_menu_send,
            "Reply",
            replyPendingIntent
        ).addRemoteInput(remoteInput).build()

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_notify_chat)
            .setStyle(messagingStyle)
            .setContentIntent(pendingIntent)
            .addAction(replyAction)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)

        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        manager.notify(NOTIFICATION_ID, builder.build())
    }
}
