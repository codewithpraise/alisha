package com.friendos.alishabubbzieee.ui.components

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.dp
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme

/**
 * 3-dot organic typing indicator.
 * Staggered phase offset (1.6s cycle), alive and breathing.
 */
@Composable
fun TypingIndicator(
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "TypingTransition")

    @Composable
    fun animateDot(delayMillis: Int): Pair<Float, Float> {
        val scale by infiniteTransition.animateFloat(
            initialValue = 0.65f,
            targetValue = 1.15f,
            animationSpec = infiniteRepeatable(
                animation = tween(800, delayMillis = delayMillis, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse
            ),
            label = "DotScale_$delayMillis"
        )
        val alpha by infiniteTransition.animateFloat(
            initialValue = 0.35f,
            targetValue = 0.95f,
            animationSpec = infiniteRepeatable(
                animation = tween(800, delayMillis = delayMillis, easing = FastOutSlowInEasing),
                repeatMode = RepeatMode.Reverse
            ),
            label = "DotAlpha_$delayMillis"
        )
        return Pair(scale, alpha)
    }

    val dot1 = animateDot(0)
    val dot2 = animateDot(260)
    val dot3 = animateDot(520)

    Box(
        modifier = modifier
            .background(
                color = AlishaTheme.colors.bgBubbleAlisha,
                shape = AlishaTheme.shapes.bubbleAlisha
            )
            .padding(horizontal = 16.dp, vertical = 14.dp)
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            listOf(dot1, dot2, dot3).forEach { (scale, alpha) ->
                Box(
                    modifier = Modifier
                        .size(6.dp)
                        .scale(scale)
                        .background(
                            color = AlishaTheme.colors.accent.copy(alpha = alpha),
                            shape = CircleShape
                        )
                )
            }
        }
    }
}
