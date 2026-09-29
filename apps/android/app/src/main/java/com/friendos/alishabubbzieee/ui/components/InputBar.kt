package com.friendos.alishabubbzieee.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.scaleIn
import androidx.compose.animation.scaleOut
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.BasicTextField
import com.friendos.alishabubbzieee.ui.theme.AlishaIcons
import androidx.compose.material3.Divider
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme
import kotlinx.coroutines.delay
import kotlin.math.roundToInt

/**
 * Floating Input Bar with Morphing Voice Recording Bar.
 * Floats above keyboard on bg_elevated with 20dp top corners.
 * Placeholder: "say something..."
 */
@Composable
fun InputBar(
    modifier: Modifier = Modifier,
    inputText: String,
    onInputTextChange: (String) -> Unit,
    onSendMessage: (String) -> Unit,
    onVoiceSend: (Float) -> Unit,
    isRecording: Boolean = false,
    onStartRecording: () -> Unit = {},
    onStopRecording: () -> Unit = {},
    onCancelRecording: () -> Unit = {},
    recordingAmplitude: Float = 0.3f
) {
    var recordingSeconds by remember { mutableIntStateOf(0) }
    var dragOffsetX by remember { mutableFloatStateOf(0f) }
    var inlineWhisper by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(isRecording) {
        if (isRecording) {
            recordingSeconds = 0
            dragOffsetX = 0f
            while (true) {
                delay(1000)
                recordingSeconds++
            }
        }
    }

    // Clear inline whisper after 3.5s
    LaunchedEffect(inlineWhisper) {
        if (inlineWhisper != null) {
            delay(3500)
            inlineWhisper = null
        }
    }

    Column(
        modifier = modifier
            .fillMaxWidth()
            .background(
                color = AlishaTheme.colors.bgElevated,
                shape = AlishaTheme.shapes.inputBar
            )
    ) {
        // Hairline top divider
        HorizontalDivider(
            thickness = 0.5.dp,
            color = AlishaTheme.colors.divider
        )

        // Inline gentle whisper notification (e.g. "too quick — didn't catch that")
        AnimatedVisibility(
            visible = inlineWhisper != null,
            enter = fadeIn(),
            exit = fadeOut()
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 6.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = inlineWhisper ?: "",
                    style = AlishaTheme.typography.conversationText,
                    color = AlishaTheme.colors.textSecondary
                )
            }
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp)
        ) {
            if (isRecording) {
                // Morphing Recording Bar with live mirrored amplitude waveform
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .offset { IntOffset(dragOffsetX.roundToInt().coerceAtMost(0), 0) }
                        .pointerInput(Unit) {
                            detectDragGestures(
                                onDragEnd = {
                                    if (dragOffsetX < -180f) {
                                        onCancelRecording()
                                    }
                                    dragOffsetX = 0f
                                },
                                onDragCancel = { dragOffsetX = 0f },
                                onDrag = { change, dragAmount ->
                                    change.consume()
                                    dragOffsetX += dragAmount.x
                                }
                            )
                        },
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Pulsing recording dot & elapsed time
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        BreathingDot(
                            dotSize = 7.dp,
                            color = AlishaTheme.colors.danger
                        )
                        Text(
                            text = String.format("0:%02d", recordingSeconds),
                            style = AlishaTheme.typography.timestamp,
                            color = AlishaTheme.colors.textPrimary
                        )
                    }

                    // Live waveform preview
                    WaveformView(
                        modifier = Modifier
                            .weight(1f)
                            .padding(horizontal = 12.dp),
                        amplitudes = List(24) { (recordingAmplitude * (0.4f + (it % 5) * 0.15f)).coerceIn(0.1f, 1f) },
                        isPlaying = true,
                        accentColor = AlishaTheme.colors.accent,
                        height = 24.dp
                    )

                    // Slide to cancel affordance
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Icon(
                            imageVector = AlishaIcons.ArrowBack,
                            contentDescription = "Cancel",
                            tint = AlishaTheme.colors.textSecondary,
                            modifier = Modifier.size(14.dp)
                        )
                        Text(
                            text = "swipe to cancel",
                            style = AlishaTheme.typography.labelSmall,
                            color = AlishaTheme.colors.textSecondary
                        )
                    }

                    // Stop / Send recording button
                    IconButton(
                        onClick = {
                            if (recordingSeconds < 1) {
                                inlineWhisper = "too quick — didn't catch that"
                                onCancelRecording()
                            } else {
                                onStopRecording()
                                onVoiceSend(recordingSeconds.toFloat())
                            }
                        },
                        modifier = Modifier
                            .size(36.dp)
                            .background(AlishaTheme.colors.accent, CircleShape)
                    ) {
                        Icon(
                            imageVector = AlishaIcons.Stop,
                            contentDescription = "Done",
                            tint = AlishaTheme.colors.bgBase,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            } else {
                // Standard text input bar
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Box(
                        modifier = Modifier.weight(1f),
                        contentAlignment = Alignment.CenterStart
                    ) {
                        if (inputText.isEmpty()) {
                            Text(
                                text = "say something…",
                                style = AlishaTheme.typography.inputPlaceholder,
                                color = AlishaTheme.colors.textSecondary.copy(alpha = 0.65f)
                            )
                        }
                        BasicTextField(
                            value = inputText,
                            onValueChange = onInputTextChange,
                            textStyle = AlishaTheme.typography.conversationText.copy(
                                color = AlishaTheme.colors.textPrimary
                            ),
                            cursorBrush = SolidColor(AlishaTheme.colors.accent),
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    // Voice / Mic Trigger
                    IconButton(
                        onClick = onStartRecording,
                        modifier = Modifier.size(36.dp)
                    ) {
                        Icon(
                            imageVector = AlishaIcons.Mic,
                            contentDescription = "Voice note",
                            tint = AlishaTheme.colors.textSecondary,
                            modifier = Modifier.size(22.dp)
                        )
                    }

                    // Send Button: filled accent circle, 40dp, animated in
                    AnimatedVisibility(
                        visible = inputText.trim().isNotEmpty(),
                        enter = fadeIn() + scaleIn(spring(stiffness = Spring.StiffnessLow)),
                        exit = fadeOut() + scaleOut()
                    ) {
                        IconButton(
                            onClick = {
                                if (inputText.isNotBlank()) {
                                    val toSend = inputText.trim()
                                    onSendMessage(toSend)
                                    onInputTextChange("")
                                }
                            },
                            modifier = Modifier
                                .size(38.dp)
                                .background(AlishaTheme.colors.accent, CircleShape)
                        ) {
                            Icon(
                                imageVector = AlishaIcons.ArrowUpward,
                                contentDescription = "Send",
                                tint = AlishaTheme.colors.bgBase,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}
