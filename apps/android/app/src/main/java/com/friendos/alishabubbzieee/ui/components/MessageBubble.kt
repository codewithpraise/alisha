package com.friendos.alishabubbzieee.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.CircleShape
import com.friendos.alishabubbzieee.ui.theme.AlishaIcons
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.withStyle
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.friendos.alishabubbzieee.ui.theme.AlishaMotion
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme

data class MessageUiModel(
    val id: String,
    val sender: String, // "alisha" or "user"
    val content: String,
    val timestampMs: Long,
    val isVoice: Boolean = false,
    val audioDurationSec: Float = 0f,
    val audioAmplitudes: List<Float> = emptyList()
)

/**
 * The Signature Asymmetric Message Bubble.
 * Alisha: top-left 24dp, top-right 12dp, bottom corners 4dp with subtle top edge lamplight glow.
 * User: sharp top, soft bottom. Leans toward Alisha.
 * Supports: TTS word-by-word highlight in accent color.
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun MessageBubble(
    message: MessageUiModel,
    isFirstInBurst: Boolean = true,
    isLastInBurst: Boolean = true,
    showPresenceDot: Boolean = false,
    currentSpokenWordIndex: Int = -1, // For word-by-word TTS highlight
    isPlayingVoice: Boolean = false,
    voicePlayProgress: Float = 0f,
    onVoicePlayToggle: () -> Unit = {},
    onLongPress: () -> Unit = {}
) {
    val haptic = LocalHapticFeedback.current
    var isPressed by remember { mutableStateOf(false) }

    val isAlisha = message.sender.lowercase() == "alisha" || message.sender.lowercase() == "assistant"
    val bubbleShape = if (isAlisha) AlishaTheme.shapes.bubbleAlisha else AlishaTheme.shapes.bubbleUser
    val bubbleBg = if (isAlisha) AlishaTheme.colors.bgBubbleAlisha else AlishaTheme.colors.bgBubbleUser
    val textColor = if (isAlisha) AlishaTheme.colors.textAlisha else AlishaTheme.colors.textUser

    val scale by animateFloatAsState(
        targetValue = if (isPressed) 0.97f else 1.0f,
        animationSpec = tween(120, easing = FastOutSlowInEasing),
        label = "BubblePressScale"
    )

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                horizontal = 16.dp,
                vertical = if (isFirstInBurst) 6.dp else 2.dp
            ),
        horizontalArrangement = if (isAlisha) Arrangement.Start else Arrangement.End,
        verticalAlignment = Alignment.Bottom
    ) {
        // Presence Dot on Alisha's leading edge
        if (isAlisha) {
            if (showPresenceDot && isLastInBurst) {
                BreathingDot(
                    modifier = Modifier.padding(bottom = 6.dp, end = 6.dp),
                    dotSize = 5.dp
                )
            } else {
                Spacer(modifier = Modifier.width(11.dp))
            }
        }

        Box(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .scale(scale)
                .background(bubbleBg, bubbleShape)
                .then(
                    if (isAlisha) {
                        // Subtle 1.5dp warm glow lamplight border on top edge
                        Modifier.border(1.dp, AlishaTheme.colors.warmGlow, bubbleShape)
                    } else {
                        Modifier
                    }
                )
                .combinedClickable(
                    onClick = {
                        if (message.isVoice) {
                            onVoicePlayToggle()
                        }
                    },
                    onLongClick = {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onLongPress()
                    }
                )
                .padding(horizontal = 14.dp, vertical = 10.dp)
        ) {
            if (message.isVoice) {
                // Voice note UI with animated waveform & play/pause toggle
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .background(AlishaTheme.colors.accent, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = if (isPlayingVoice) AlishaIcons.Pause else AlishaIcons.PlayArrow,
                            contentDescription = if (isPlayingVoice) "Pause" else "Play",
                            tint = AlishaTheme.colors.bgBase,
                            modifier = Modifier.size(18.dp)
                        )
                    }

                    Column(modifier = Modifier.weight(1f)) {
                        WaveformView(
                            amplitudes = message.audioAmplitudes,
                            isPlaying = isPlayingVoice,
                            playProgress = voicePlayProgress,
                            accentColor = AlishaTheme.colors.accent,
                            height = 24.dp
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = String.format("%.1fs", message.audioDurationSec),
                            style = AlishaTheme.typography.timestamp,
                            color = AlishaTheme.colors.textSecondary
                        )
                    }
                }
            } else {
                // Text Message with TTS Word-by-Word Synchronized Highlight
                if (isAlisha && currentSpokenWordIndex >= 0) {
                    val words = remember(message.content) { message.content.split(Regex("\\s+")) }
                    val annotatedString = buildAnnotatedString {
                        words.forEachIndexed { index, word ->
                            if (index == currentSpokenWordIndex) {
                                withStyle(
                                    SpanStyle(
                                        color = AlishaTheme.colors.accent,
                                        fontSize = 17.2.sp
                                    )
                                ) {
                                    append(word)
                                }
                            } else {
                                withStyle(SpanStyle(color = textColor)) {
                                    append(word)
                                }
                            }
                            if (index < words.size - 1) append(" ")
                        }
                    }
                    Text(
                        text = annotatedString,
                        style = AlishaTheme.typography.alishaText
                    )
                } else {
                    Text(
                        text = message.content,
                        style = if (isAlisha) AlishaTheme.typography.alishaText else AlishaTheme.typography.conversationText,
                        color = textColor
                    )
                }
            }
        }
    }
}
