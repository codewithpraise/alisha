package com.friendos.alishabubbzieee.ui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.friendos.alishabubbzieee.ui.theme.AlishaMotion
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme

/**
 * The Signature Breathing Dot (The App's Heartbeat).
 * 4dp accent dot with a 4-second organic inhale/exhale cycle.
 * Pauses during user typing, pulses gently when Alisha is "present".
 */
@Composable
fun BreathingDot(
    modifier: Modifier = Modifier,
    dotSize: Dp = 6.dp,
    color: Color = AlishaTheme.colors.accent,
    isBreathing: Boolean = true,
    showAura: Boolean = true
) {
    val infiniteTransition = rememberInfiniteTransition(label = "BreathingDotTransition")

    val scale by infiniteTransition.animateFloat(
        initialValue = 0.85f,
        targetValue = 1.25f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = AlishaMotion.PresenceBreathingDuration / 2,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "BreathScale"
    )

    val alpha by infiniteTransition.animateFloat(
        initialValue = 0.45f,
        targetValue = 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = AlishaMotion.PresenceBreathingDuration / 2,
                easing = FastOutSlowInEasing
            ),
            repeatMode = RepeatMode.Reverse
        ),
        label = "BreathAlpha"
    )

    val currentScale = if (isBreathing) scale else 1.0f
    val currentAlpha = if (isBreathing) alpha else 0.85f

    Box(
        modifier = modifier.size(dotSize * 2.5f),
        contentAlignment = Alignment.Center
    ) {
        if (showAura && isBreathing) {
            // Soft glowing lamplight aura
            Box(
                modifier = Modifier
                    .size(dotSize * 2.2f)
                    .scale(currentScale * 1.3f)
                    .background(color.copy(alpha = currentAlpha * 0.22f), CircleShape)
            )
        }

        // Core presence dot
        Box(
            modifier = Modifier
                .size(dotSize)
                .scale(currentScale)
                .background(color.copy(alpha = currentAlpha), CircleShape)
        )
    }
}
