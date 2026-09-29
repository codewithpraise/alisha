package com.friendos.alishabubbzieee.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.friendos.alishabubbzieee.ui.components.BreathingDot
import com.friendos.alishabubbzieee.ui.components.WaveformView
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme

/**
 * 3-Screen Human Onboarding (<45 seconds total).
 * Warm, lowercase, intimate.
 * Screen 1: "hey. i'm alisha." -> "okay, hi"
 * Screen 2: "what should i call you?" -> single name field
 * Screen 3: "and do you want to hear my voice, or just text?" -> 2 touch targets
 */
@Composable
fun OnboardingScreen(
    onComplete: (userName: String, enableVoice: Boolean) -> Unit
) {
    var step by remember { mutableIntStateOf(1) }
    var userName by remember { mutableStateOf("") }
    var enableVoice by remember { mutableStateOf(true) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(AlishaTheme.colors.bgBase)
            .statusBarsPadding()
            .padding(horizontal = 32.dp),
        contentAlignment = Alignment.Center
    ) {
        AnimatedContent(
            targetState = step,
            transitionSpec = { fadeIn() togetherWith fadeOut() },
            label = "OnboardingStep"
        ) { currentStep ->
            when (currentStep) {
                1 -> {
                    // Screen 1: Breathing dot + "hey. i'm alisha."
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        BreathingDot(
                            dotSize = 10.dp,
                            color = AlishaTheme.colors.accent
                        )
                        Spacer(modifier = Modifier.height(28.dp))
                        Text(
                            text = "hey. i'm alisha.",
                            style = AlishaTheme.typography.conversationText.copy(fontSize = 22.sp),
                            color = AlishaTheme.colors.textPrimary
                        )
                        Spacer(modifier = Modifier.height(48.dp))
                        Box(
                            modifier = Modifier
                                .background(AlishaTheme.colors.accent, RoundedCornerShape(24.dp))
                                .clickable { step = 2 }
                                .padding(horizontal = 28.dp, vertical = 12.dp)
                        ) {
                            Text(
                                text = "okay, hi",
                                style = AlishaTheme.typography.conversationText,
                                color = AlishaTheme.colors.bgBase
                            )
                        }
                    }
                }
                2 -> {
                    // Screen 2: "what should i call you?"
                    Column(
                        horizontalAlignment = Alignment.Start,
                        verticalArrangement = Arrangement.Center,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = "what should i call you?",
                            style = AlishaTheme.typography.conversationText.copy(fontSize = 20.sp),
                            color = AlishaTheme.colors.textPrimary
                        )
                        Spacer(modifier = Modifier.height(20.dp))
                        BasicTextField(
                            value = userName,
                            onValueChange = { userName = it },
                            textStyle = AlishaTheme.typography.conversationText.copy(
                                color = AlishaTheme.colors.accent,
                                fontSize = 24.sp
                            ),
                            cursorBrush = SolidColor(AlishaTheme.colors.accent),
                            modifier = Modifier.fillMaxWidth(),
                            decorationBox = { innerTextField ->
                                Column {
                                    innerTextField()
                                    Spacer(modifier = Modifier.height(6.dp))
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(1.5.dp)
                                            .background(AlishaTheme.colors.accent)
                                    )
                                }
                            }
                        )
                        Spacer(modifier = Modifier.height(40.dp))
                        Box(
                            modifier = Modifier
                                .align(Alignment.End)
                                .background(
                                    color = if (userName.trim().isNotEmpty()) AlishaTheme.colors.accent else AlishaTheme.colors.bgElevated,
                                    shape = RoundedCornerShape(20.dp)
                                )
                                .clickable(enabled = userName.trim().isNotEmpty()) { step = 3 }
                                .padding(horizontal = 22.dp, vertical = 10.dp)
                        ) {
                            Text(
                                text = "next",
                                style = AlishaTheme.typography.conversationText,
                                color = if (userName.trim().isNotEmpty()) AlishaTheme.colors.bgBase else AlishaTheme.colors.textSecondary
                            )
                        }
                    }
                }
                3 -> {
                    // Screen 3: "and do you want to hear my voice, or just text?"
                    Column(
                        horizontalAlignment = Alignment.Start,
                        verticalArrangement = Arrangement.Center,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(
                            text = "and do you want to hear my voice, or just text?",
                            style = AlishaTheme.typography.conversationText.copy(fontSize = 19.sp),
                            color = AlishaTheme.colors.textPrimary
                        )
                        Spacer(modifier = Modifier.height(28.dp))

                        // Voice Choice
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(AlishaTheme.colors.bgElevated, RoundedCornerShape(16.dp))
                                .border(
                                    width = if (enableVoice) 1.5.dp else 0.dp,
                                    color = if (enableVoice) AlishaTheme.colors.accent else androidx.compose.ui.graphics.Color.Transparent,
                                    shape = RoundedCornerShape(16.dp)
                                )
                                .clickable { enableVoice = true }
                                .padding(18.dp)
                        ) {
                            Column {
                                Text(
                                    text = "voice & text",
                                    style = AlishaTheme.typography.conversationText,
                                    color = AlishaTheme.colors.textPrimary
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                WaveformView(
                                    amplitudes = List(24) { (0.3f + (it % 4) * 0.15f) },
                                    accentColor = AlishaTheme.colors.accent,
                                    height = 18.dp
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(14.dp))

                        // Text Only Choice
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .background(AlishaTheme.colors.bgElevated, RoundedCornerShape(16.dp))
                                .border(
                                    width = if (!enableVoice) 1.5.dp else 0.dp,
                                    color = if (!enableVoice) AlishaTheme.colors.accent else androidx.compose.ui.graphics.Color.Transparent,
                                    shape = RoundedCornerShape(16.dp)
                                )
                                .clickable { enableVoice = false }
                                .padding(18.dp)
                        ) {
                            Text(
                                text = "just text",
                                style = AlishaTheme.typography.conversationText,
                                color = AlishaTheme.colors.textPrimary
                            )
                        }

                        Spacer(modifier = Modifier.height(36.dp))

                        Box(
                            modifier = Modifier
                                .align(Alignment.End)
                                .background(AlishaTheme.colors.accent, RoundedCornerShape(20.dp))
                                .clickable {
                                    val finalName = if (userName.isBlank()) "friend" else userName.trim()
                                    onComplete(finalName, enableVoice)
                                }
                                .padding(horizontal = 24.dp, vertical = 10.dp)
                        ) {
                            Text(
                                text = "let's go",
                                style = AlishaTheme.typography.conversationText,
                                color = AlishaTheme.colors.bgBase
                            )
                        }
                    }
                }
            }
        }
    }
}
