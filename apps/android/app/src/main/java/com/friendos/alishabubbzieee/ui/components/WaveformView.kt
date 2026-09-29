package com.friendos.alishabubbzieee.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme
import kotlin.math.abs
import kotlin.math.sin

/**
 * 24-bar mirrored audio amplitude waveform.
 * Renders live amplitude during recording, interactive playhead dot during playback.
 */
@Composable
fun WaveformView(
    modifier: Modifier = Modifier,
    amplitudes: List<Float> = emptyList(),
    isPlaying: Boolean = false,
    playProgress: Float = 0f, // 0.0 to 1.0
    barCount: Int = 24,
    height: Dp = 38.dp,
    accentColor: Color = AlishaTheme.colors.accent,
    inactiveColor: Color = AlishaTheme.colors.textSecondary.copy(alpha = 0.45f),
    onSeek: ((Float) -> Unit)? = null
) {
    val infiniteTransition = rememberInfiniteTransition(label = "WaveformAnimation")
    val phase by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = (2 * Math.PI).toFloat(),
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "WavePhase"
    )

    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(height)
            .pointerInput(Unit) {
                if (onSeek != null) {
                    detectTapGestures { offset ->
                        val progress = (offset.x / size.width).coerceIn(0f, 1f)
                        onSeek(progress)
                    }
                }
            }
    ) {
        Canvas(modifier = Modifier.matchParentSize()) {
            val totalWidth = size.width
            val totalHeight = size.height
            val centerY = totalHeight / 2f
            val spacing = 3.dp.toPx()
            val totalSpacing = spacing * (barCount - 1)
            val barWidth = ((totalWidth - totalSpacing) / barCount).coerceAtLeast(2.dp.toPx())

            for (i in 0 until barCount) {
                val x = i * (barWidth + spacing)

                // Calculate bar normalized height (0.15 to 1.0)
                val baseAmp = if (i < amplitudes.size) {
                    amplitudes[i].coerceIn(0.12f, 1.0f)
                } else {
                    val staticPattern = abs(sin((i * 0.42f) + 0.3f)) * 0.7f + 0.25f
                    if (isPlaying) {
                        val dynamicFactor = abs(sin(phase + i * 0.35f)) * 0.4f
                        (staticPattern + dynamicFactor).coerceIn(0.15f, 1.0f)
                    } else {
                        staticPattern
                    }
                }

                val barH = (totalHeight * 0.85f * baseAmp).coerceAtLeast(4.dp.toPx())
                val top = centerY - (barH / 2f)

                // Color based on playhead progress
                val barProgress = i.toFloat() / (barCount - 1)
                val isPastPlayhead = isPlaying && barProgress <= playProgress
                val color = if (isPastPlayhead) accentColor else inactiveColor

                drawRoundRect(
                    color = color,
                    topLeft = Offset(x, top),
                    size = Size(barWidth, barH),
                    cornerRadius = CornerRadius(barWidth / 2f, barWidth / 2f)
                )

                // Render soft playhead indicator dot
                if (isPlaying && abs(barProgress - playProgress) < (1f / barCount)) {
                    drawCircle(
                        color = accentColor,
                        radius = 4.dp.toPx(),
                        center = Offset(x + (barWidth / 2f), centerY)
                    )
                }
            }
        }
    }
}
