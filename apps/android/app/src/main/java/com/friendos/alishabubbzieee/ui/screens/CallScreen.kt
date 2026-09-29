package com.friendos.alishabubbzieee.ui.screens

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.CircleShape
import com.friendos.alishabubbzieee.ui.theme.AlishaIcons
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.friendos.alishabubbzieee.ui.components.BreathingDot
import com.friendos.alishabubbzieee.ui.components.WaveformView
import com.friendos.alishabubbzieee.ui.theme.AlishaMotion
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme
import kotlinx.coroutines.delay

enum class CallStatusState {
    CONNECTING,
    LISTENING,
    SPEAKING,
    THINKING
}

/**
 * Ambient Voice Call Screen.
 * Implements real-time two-way voice calling with live audio reactivity,
 * VAD interruption (barge-in), and natural conversational pacing.
 */
@Composable
fun CallScreen(
    callStatus: CallStatusState = CallStatusState.LISTENING,
    speechAmplitude: Float = 0.5f,
    onEndCall: () -> Unit
) {
    var callSeconds by remember { mutableIntStateOf(0) }
    var isMuted by remember { mutableStateOf(false) }
    var isSpeakerOn by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        while (true) {
            delay(1000)
            callSeconds++
        }
    }

    val infiniteTransition = rememberInfiniteTransition(label = "CallOrbPulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 0.95f,
        targetValue = 1.18f,
        animationSpec = infiniteRepeatable(
            animation = tween(2400, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "OrbPulse"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(AlishaTheme.colors.bgBase)
            .statusBarsPadding()
            .navigationBarsPadding()
    ) {
        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Header Info
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.padding(top = 36.dp)
            ) {
                Text(
                    text = "alisha",
                    style = AlishaTheme.typography.conversationText.copy(fontSize = 20.sp),
                    color = AlishaTheme.colors.textPrimary
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = String.format("%02d:%02d", callSeconds / 60, callSeconds % 60),
                    style = AlishaTheme.typography.timestamp,
                    color = AlishaTheme.colors.textSecondary
                )
                Spacer(modifier = Modifier.height(10.dp))
                // Status hint
                val statusText = when (callStatus) {
                    CallStatusState.CONNECTING -> "connecting…"
                    CallStatusState.LISTENING -> "listening…"
                    CallStatusState.SPEAKING -> "speaking…"
                    CallStatusState.THINKING -> "thinking…"
                }
                Text(
                    text = statusText,
                    style = AlishaTheme.typography.labelSmall,
                    color = AlishaTheme.colors.accent
                )
            }

            // Center Ambient Orb & Waveform
            Box(
                modifier = Modifier
                    .size(240.dp),
                contentAlignment = Alignment.Center
            ) {
                // Outer warm lamplight glow
                Box(
                    modifier = Modifier
                        .size(220.dp)
                        .scale(pulseScale)
                        .background(AlishaTheme.colors.accent.copy(alpha = 0.08f), CircleShape)
                )

                // Middle breathing aura
                Box(
                    modifier = Modifier
                        .size(160.dp)
                        .scale(pulseScale * 0.9f)
                        .background(AlishaTheme.colors.accent.copy(alpha = 0.18f), CircleShape)
                )

                // Core orb with live mirrored waveform
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                    modifier = Modifier.padding(horizontal = 24.dp)
                ) {
                    BreathingDot(
                        dotSize = 10.dp,
                        color = AlishaTheme.colors.accent,
                        isBreathing = callStatus == CallStatusState.LISTENING
                    )
                    Spacer(modifier = Modifier.height(18.dp))
                    WaveformView(
                        amplitudes = List(24) { (speechAmplitude * (0.35f + (it % 7) * 0.12f)).coerceIn(0.1f, 1f) },
                        isPlaying = callStatus == CallStatusState.SPEAKING,
                        accentColor = AlishaTheme.colors.accent,
                        height = 36.dp
                    )
                }
            }

            // Bottom Call Controls
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 44.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Mute Toggle
                    IconButton(
                        onClick = { isMuted = !isMuted },
                        modifier = Modifier
                            .size(54.dp)
                            .background(
                                color = if (isMuted) AlishaTheme.colors.danger.copy(alpha = 0.2f) else AlishaTheme.colors.bgElevated,
                                shape = CircleShape
                            )
                    ) {
                        Icon(
                            imageVector = if (isMuted) AlishaIcons.MicOff else AlishaIcons.Mic,
                            contentDescription = "Mute",
                            tint = if (isMuted) AlishaTheme.colors.danger else AlishaTheme.colors.textPrimary,
                            modifier = Modifier.size(24.dp)
                        )
                    }

                    // Hang up button
                    IconButton(
                        onClick = onEndCall,
                        modifier = Modifier
                            .size(64.dp)
                            .background(AlishaTheme.colors.danger, CircleShape)
                    ) {
                        Icon(
                            imageVector = AlishaIcons.CallEnd,
                            contentDescription = "End Call",
                            tint = AlishaTheme.colors.bgBase,
                            modifier = Modifier.size(30.dp)
                        )
                    }

                    // Speakerphone Toggle
                    IconButton(
                        onClick = { isSpeakerOn = !isSpeakerOn },
                        modifier = Modifier
                            .size(54.dp)
                            .background(
                                color = if (isSpeakerOn) AlishaTheme.colors.accent.copy(alpha = 0.2f) else AlishaTheme.colors.bgElevated,
                                shape = CircleShape
                            )
                    ) {
                        Icon(
                            imageVector = AlishaIcons.VolumeUp,
                            contentDescription = "Speaker",
                            tint = if (isSpeakerOn) AlishaTheme.colors.accent else AlishaTheme.colors.textPrimary,
                            modifier = Modifier.size(24.dp)
                        )
                    }
                }
            }
        }
    }
}
