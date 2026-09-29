package com.friendos.alishabubbzieee.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.friendos.alishabubbzieee.core.controller.AlishaController
import com.friendos.alishabubbzieee.core.proactive.ProactiveMessagingWorker
import com.friendos.alishabubbzieee.core.voice.CallSessionState
import com.friendos.alishabubbzieee.core.voice.VoiceCallManager
import com.friendos.alishabubbzieee.ui.components.MessageUiModel
import com.friendos.alishabubbzieee.ui.screens.CallScreen
import com.friendos.alishabubbzieee.ui.screens.CallStatusState
import com.friendos.alishabubbzieee.ui.screens.ConversationScreen
import com.friendos.alishabubbzieee.ui.screens.OnboardingScreen
import com.friendos.alishabubbzieee.ui.screens.SettingsScreen
import com.friendos.alishabubbzieee.ui.theme.AlishaMotion
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.UUID
import java.util.concurrent.TimeUnit

enum class AppScreen {
    CONVERSATION,
    CALL,
    SETTINGS,
    ONBOARDING
}

class MainActivity : ComponentActivity() {

    private val controller = AlishaController()

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { _ -> }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Request audio & notification permissions
        val permissions = mutableListOf(Manifest.permission.RECORD_AUDIO)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        val needed = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (needed.isNotEmpty()) {
            requestPermissionLauncher.launch(needed.toTypedArray())
        }

        // Schedule autonomous unprompted messaging
        scheduleProactiveMessaging()

        setContent {
            var isDimMode by remember { mutableStateOf(false) }
            var currentScreen by remember { mutableStateOf(AppScreen.CONVERSATION) }
            val messages = remember { mutableStateListOf<MessageUiModel>() }
            var isAlishaTyping by remember { mutableStateOf(false) }
            var activeSpeakingMsgId by remember { mutableStateOf<String?>(null) }
            var currentSpokenWordIndex by remember { mutableIntStateOf(-1) }

            val scope = rememberCoroutineScope()

            val callManager = remember {
                VoiceCallManager(scope) { spokenText ->
                    // Spoken reply in call
                }
            }
            val callSessionState by callManager.callState.collectAsState()
            val callAmplitude by callManager.amplitude.collectAsState()

            AlishaTheme(isDimMode = isDimMode) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(AlishaTheme.colors.bgBase)
                ) {
                    AnimatedContent(
                        targetState = currentScreen,
                        transitionSpec = { fadeIn() togetherWith fadeOut() },
                        label = "ScreenTransition"
                    ) { screen ->
                        when (screen) {
                            AppScreen.CONVERSATION -> {
                                ConversationScreen(
                                    messages = messages,
                                    isAlishaTyping = isAlishaTyping,
                                    activeSpeakingMessageId = activeSpeakingMsgId,
                                    currentSpokenWordIndex = currentSpokenWordIndex,
                                    onSendMessage = { userText ->
                                        // 1. Add user message bubble
                                        val userMsg = MessageUiModel(
                                            id = UUID.randomUUID().toString(),
                                            sender = "user",
                                            content = userText,
                                            timestampMs = System.currentTimeMillis()
                                        )
                                        messages.add(userMsg)

                                        // 2. Trigger Alisha typing & response
                                        scope.launch {
                                            isAlishaTyping = true
                                            delay(500) // Natural typing latency

                                            // Local controller handles GREET / FROZEN short-circuit & LLM
                                            val bursts = controller.reply(userText) { prompt ->
                                                // Fallback on-device deterministic mock when llama binary not mounted in emulator
                                                "i'm thinking of where i put my phone"
                                            }

                                            isAlishaTyping = false

                                            // 3. Stagger burst bubbles at 90ms intervals
                                            bursts.forEachIndexed { i, burstText ->
                                                if (i > 0) delay(AlishaMotion.StaggerBurstInterval.toLong())
                                                val alishaMsg = MessageUiModel(
                                                    id = UUID.randomUUID().toString(),
                                                    sender = "alisha",
                                                    content = burstText,
                                                    timestampMs = System.currentTimeMillis()
                                                )
                                                messages.add(alishaMsg)

                                                // 4. Word-by-word synchronized TTS highlight for the reply
                                                launch {
                                                    activeSpeakingMsgId = alishaMsg.id
                                                    val words = burstText.split(Regex("\\s+"))
                                                    words.forEachIndexed { wordIdx, _ ->
                                                        currentSpokenWordIndex = wordIdx
                                                        delay(AlishaMotion.WordHighlightCrossfade.toLong() * 2)
                                                    }
                                                    delay(200)
                                                    activeSpeakingMsgId = null
                                                    currentSpokenWordIndex = -1
                                                }
                                            }
                                        }
                                    },
                                    onVoiceSend = { durationSec ->
                                        val voiceMsg = MessageUiModel(
                                            id = UUID.randomUUID().toString(),
                                            sender = "user",
                                            content = "[voice note]",
                                            timestampMs = System.currentTimeMillis(),
                                            isVoice = true,
                                            audioDurationSec = durationSec,
                                            audioAmplitudes = List(24) { 0.4f + (it % 4) * 0.15f }
                                        )
                                        messages.add(voiceMsg)
                                    },
                                    onOpenCall = {
                                        callManager.startCall()
                                        currentScreen = AppScreen.CALL
                                    },
                                    onOpenSettings = {
                                        currentScreen = AppScreen.SETTINGS
                                    },
                                    onDeleteMessage = { msgId ->
                                        messages.removeAll { it.id == msgId }
                                    }
                                )
                            }
                            AppScreen.CALL -> {
                                CallScreen(
                                    callStatus = when (callSessionState) {
                                        CallSessionState.IDLE -> CallStatusState.CONNECTING
                                        CallSessionState.LISTENING -> CallStatusState.LISTENING
                                        CallSessionState.SPEAKING -> CallStatusState.SPEAKING
                                        CallSessionState.THINKING -> CallStatusState.THINKING
                                    },
                                    speechAmplitude = callAmplitude,
                                    onEndCall = {
                                        callManager.endCall()
                                        currentScreen = AppScreen.CONVERSATION
                                    }
                                )
                            }
                            AppScreen.SETTINGS -> {
                                SettingsScreen(
                                    isDimMode = isDimMode,
                                    onToggleDimMode = { isDimMode = it },
                                    onBack = { currentScreen = AppScreen.CONVERSATION },
                                    onClearConversation = {
                                        messages.clear()
                                        controller.reset()
                                    }
                                )
                            }
                            AppScreen.ONBOARDING -> {
                                OnboardingScreen(
                                    onComplete = { _, _ ->
                                        currentScreen = AppScreen.CONVERSATION
                                    }
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    private fun scheduleProactiveMessaging() {
        val proactiveWork = PeriodicWorkRequestBuilder<ProactiveMessagingWorker>(
            3, TimeUnit.HOURS
        ).build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "AlishaAutonomousCompanion",
            ExistingPeriodicWorkPolicy.KEEP,
            proactiveWork
        )
    }
}
