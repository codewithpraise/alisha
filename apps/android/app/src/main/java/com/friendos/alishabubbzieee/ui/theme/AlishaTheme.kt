package com.friendos.alishabubbzieee.ui.theme

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * ALISHA DESIGN SYSTEM (v1.0)
 * Metaphor: "someone is awake with me at 2am."
 * Intimacy over density, warmth over efficiency.
 * Pure dark mode only (Dark and Dim). No pure black (#000000) or pure white (#FFFFFF).
 */
@Immutable
data class AlishaColors(
    val bgBase: Color,
    val bgElevated: Color,
    val bgBubbleAlisha: Color,
    val bgBubbleUser: Color,
    val accent: Color,
    val textPrimary: Color,
    val textSecondary: Color,
    val textAlisha: Color,
    val textUser: Color,
    val danger: Color,
    val divider: Color,
    val warmGlow: Color
)

val DarkAlishaColors = AlishaColors(
    bgBase = Color(0xFF131010),
    bgElevated = Color(0xFF1C1817),
    bgBubbleAlisha = Color(0xFF2A2422),
    bgBubbleUser = Color(0xFF3D322C),
    accent = Color(0xFFE3A587),
    textPrimary = Color(0xFFF2EDE8),
    textSecondary = Color(0xFF9A8F88),
    textAlisha = Color(0xFFF2EDE8),
    textUser = Color(0xFFF2EDE8),
    danger = Color(0xFFC4745E),
    divider = Color(0x662A2422),
    warmGlow = Color(0x1AE3A587) // 10% accent glow
)

val DimAlishaColors = AlishaColors(
    bgBase = Color(0xFF1A1615),
    bgElevated = Color(0xFF24201E),
    bgBubbleAlisha = Color(0xFF322C2A),
    bgBubbleUser = Color(0xFF453933),
    accent = Color(0xFFE8AD90),
    textPrimary = Color(0xFFF4EFEB),
    textSecondary = Color(0xFFA59B94),
    textAlisha = Color(0xFFF4EFEB),
    textUser = Color(0xFFF4EFEB),
    danger = Color(0xFFC87C67),
    divider = Color(0x73322C2A),
    warmGlow = Color(0x1FE8AD90)
)

@Immutable
data class AlishaTypography(
    val conversationText: TextStyle,
    val alishaText: TextStyle,
    val timestamp: TextStyle,
    val inputPlaceholder: TextStyle,
    val labelSmall: TextStyle,
    val titleHumanist: TextStyle
)

val LocalAlishaTypography = AlishaTypography(
    conversationText = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Normal,
        fontSize = 16.5.sp,
        lineHeight = 24.sp,
        letterSpacing = (-0.01).sp
    ),
    alishaText = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Normal,
        fontSize = 16.8.sp,
        lineHeight = 24.5.sp,
        letterSpacing = (-0.01).sp
    ),
    timestamp = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 14.sp,
        letterSpacing = 0.08.sp
    ),
    inputPlaceholder = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 22.sp
    ),
    labelSmall = TextStyle(
        fontFamily = FontFamily.Monospace,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        letterSpacing = 0.05.sp
    ),
    titleHumanist = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Medium,
        fontSize = 15.sp,
        lineHeight = 20.sp
    )
)

@Immutable
data class AlishaShapes(
    val bubbleAlisha: RoundedCornerShape,
    val bubbleUser: RoundedCornerShape,
    val inputBar: RoundedCornerShape,
    val sheet: RoundedCornerShape
)

val LocalAlishaShapes = AlishaShapes(
    // Asymmetric organic radius: top-left 24dp, top-right 12dp, bottom corners 4dp
    bubbleAlisha = RoundedCornerShape(
        topStart = 24.dp,
        topEnd = 12.dp,
        bottomStart = 4.dp,
        bottomEnd = 4.dp
    ),
    // Inverse geometry: sharp top, soft bottom
    bubbleUser = RoundedCornerShape(
        topStart = 12.dp,
        topEnd = 24.dp,
        bottomStart = 4.dp,
        bottomEnd = 4.dp
    ),
    inputBar = RoundedCornerShape(
        topStart = 20.dp,
        topEnd = 20.dp,
        bottomStart = 0.dp,
        bottomEnd = 0.dp
    ),
    sheet = RoundedCornerShape(
        topStart = 24.dp,
        topEnd = 24.dp,
        bottomStart = 0.dp,
        bottomEnd = 0.dp
    )
)

object AlishaMotion {
    val FastOutSlowIn = CubicBezierEasing(0.4f, 0.0f, 0.2f, 1.0f)
    const val MessageSendDuration = 280
    const val AlishaEntranceDuration = 340
    const val StaggerBurstInterval = 90
    const val ScreenTransitionDuration = 300
    const val TypingPulseDuration = 1600
    const val PresenceBreathingDuration = 4000
    const val WordHighlightCrossfade = 120
}

val LocalAlishaColors = staticCompositionLocalOf { DarkAlishaColors }
val LocalAlishaType = staticCompositionLocalOf { LocalAlishaTypography }
val LocalAlishaShapesProvider = staticCompositionLocalOf { LocalAlishaShapes }

object AlishaTheme {
    val colors: AlishaColors
        @Composable
        get() = LocalAlishaColors.current

    val typography: AlishaTypography
        @Composable
        get() = LocalAlishaType.current

    val shapes: AlishaShapes
        @Composable
        get() = LocalAlishaShapesProvider.current
}

@Composable
fun AlishaTheme(
    isDimMode: Boolean = false,
    content: @Composable () -> Unit
) {
    val colors = if (isDimMode) DimAlishaColors else DarkAlishaColors

    val materialColorScheme = darkColorScheme(
        background = colors.bgBase,
        surface = colors.bgElevated,
        primary = colors.accent,
        onBackground = colors.textPrimary,
        onSurface = colors.textPrimary,
        error = colors.danger
    )

    CompositionLocalProvider(
        LocalAlishaColors provides colors,
        LocalAlishaType provides LocalAlishaTypography,
        LocalAlishaShapesProvider provides LocalAlishaShapes
    ) {
        MaterialTheme(
            colorScheme = materialColorScheme,
            content = content
        )
    }
}
