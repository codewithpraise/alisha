package com.friendos.alishabubbzieee.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import com.friendos.alishabubbzieee.ui.theme.AlishaIcons
import androidx.compose.material3.Divider
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.friendos.alishabubbzieee.ui.components.WaveformView
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme

data class VoiceClipItem(
    val id: String,
    val title: String,
    val durationText: String,
    val amplitudes: List<Float>
)

/**
 * Settings Screen (Spartan, Hidden Depth).
 * Entry from top right gear icon.
 * Features:
 * - Voice reference clip picker + speech speed slider (default 0.92x for natural pacing)
 * - Dark / Dim theme toggle
 * - Hold-to-record vs tap-to-toggle
 * - Collapsible Advanced LLM sampling sliders with Reset action
 * - Database export & clear conversation
 * - Quiet footer: "everything stays on this phone."
 */
@Composable
fun SettingsScreen(
    isDimMode: Boolean,
    onToggleDimMode: (Boolean) -> Unit,
    onBack: () -> Unit,
    onClearConversation: () -> Unit
) {
    var voiceSpeed by remember { mutableFloatStateOf(0.92f) } // Default 0.92x as requested for natural pacing
    var isVoiceEnabled by remember { mutableStateOf(true) }
    var isHoldToRecord by remember { mutableStateOf(false) }
    var selectedClipId by remember { mutableStateOf("1191666156166874_seg03") }
    var isAdvancedExpanded by remember { mutableStateOf(false) }

    // Sampling params (SHIP_NOTES frozen defaults)
    var temp by remember { mutableFloatStateOf(0.75f) }
    var topP by remember { mutableFloatStateOf(0.90f) }
    var minP by remember { mutableFloatStateOf(0.05f) }
    var maxTokens by remember { mutableFloatStateOf(60f) }

    var isConfirmingClear by remember { mutableStateOf(false) }

    val sampleClips = listOf(
        VoiceClipItem("1191666156166874_seg03", "reference 01 (warm casual)", "7.4s", List(24) { (0.3f + (it % 4) * 0.15f) }),
        VoiceClipItem("1303735758283391", "reference 02 (teasing tone)", "5.2s", List(24) { (0.4f + (it % 5) * 0.12f) }),
        VoiceClipItem("1211480357481077", "reference 03 (late night)", "6.8s", List(24) { (0.25f + (it % 3) * 0.2f) })
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(AlishaTheme.colors.bgBase)
            .statusBarsPadding()
    ) {
        Column(modifier = Modifier.fillMaxSize()) {
            // Header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                IconButton(onClick = onBack) {
                    Icon(
                        imageVector = AlishaIcons.ArrowBack,
                        contentDescription = "Back",
                        tint = AlishaTheme.colors.textPrimary
                    )
                }
                Text(
                    text = "settings",
                    style = AlishaTheme.typography.conversationText.copy(fontSize = 18.sp),
                    color = AlishaTheme.colors.textPrimary
                )
            }

            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 24.dp),
                verticalArrangement = Arrangement.spacedBy(24.dp)
            ) {
                // Section 1: Voice
                item {
                    Text(
                        text = "VOICE",
                        style = AlishaTheme.typography.labelSmall,
                        color = AlishaTheme.colors.accent
                    )
                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Spoken voice replies",
                            style = AlishaTheme.typography.conversationText,
                            color = AlishaTheme.colors.textPrimary
                        )
                        Switch(
                            checked = isVoiceEnabled,
                            onCheckedChange = { isVoiceEnabled = it },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = AlishaTheme.colors.bgBase,
                                checkedTrackColor = AlishaTheme.colors.accent,
                                uncheckedThumbColor = AlishaTheme.colors.textSecondary,
                                uncheckedTrackColor = AlishaTheme.colors.bgElevated
                            )
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    // Speech Speed Slider
                    Text(
                        text = "Pacing & tempo (${String.format("%.2f", voiceSpeed)}×)",
                        style = AlishaTheme.typography.conversationText,
                        color = AlishaTheme.colors.textPrimary
                    )
                    Slider(
                        value = voiceSpeed,
                        onValueChange = { voiceSpeed = it },
                        valueRange = 0.80f..1.30f,
                        colors = SliderDefaults.colors(
                            thumbColor = AlishaTheme.colors.accent,
                            activeTrackColor = AlishaTheme.colors.accent,
                            inactiveTrackColor = AlishaTheme.colors.bgElevated
                        )
                    )

                    Spacer(modifier = Modifier.height(14.dp))
                    Text(
                        text = "Speaker Reference Clips",
                        style = AlishaTheme.typography.conversationText,
                        color = AlishaTheme.colors.textPrimary
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    // Reference Clips List
                    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        sampleClips.forEach { clip ->
                            val isSelected = clip.id == selectedClipId
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(
                                        color = if (isSelected) AlishaTheme.colors.bgElevated else AlishaTheme.colors.bgBase,
                                        shape = RoundedCornerShape(12.dp)
                                    )
                                    .clickable { selectedClipId = clip.id }
                                    .padding(horizontal = 14.dp, vertical = 10.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Text(
                                        text = clip.title,
                                        style = AlishaTheme.typography.conversationText.copy(fontSize = 15.sp),
                                        color = AlishaTheme.colors.textPrimary
                                    )
                                    Spacer(modifier = Modifier.height(4.dp))
                                    WaveformView(
                                        amplitudes = clip.amplitudes,
                                        height = 18.dp,
                                        accentColor = if (isSelected) AlishaTheme.colors.accent else AlishaTheme.colors.textSecondary
                                    )
                                }
                                if (isSelected) {
                                    Icon(
                                        imageVector = AlishaIcons.Check,
                                        contentDescription = "Selected",
                                        tint = AlishaTheme.colors.accent,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }
                            }
                        }
                    }
                }

                // Section 2: Theme
                item {
                    HorizontalDivider(thickness = 0.5.dp, color = AlishaTheme.colors.divider)
                    Spacer(modifier = Modifier.height(20.dp))
                    Text(
                        text = "APPEARANCE",
                        style = AlishaTheme.typography.labelSmall,
                        color = AlishaTheme.colors.accent
                    )
                    Spacer(modifier = Modifier.height(14.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (isDimMode) "Dim mode" else "Dark mode",
                            style = AlishaTheme.typography.conversationText,
                            color = AlishaTheme.colors.textPrimary
                        )
                        Switch(
                            checked = isDimMode,
                            onCheckedChange = onToggleDimMode,
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = AlishaTheme.colors.bgBase,
                                checkedTrackColor = AlishaTheme.colors.accent,
                                uncheckedThumbColor = AlishaTheme.colors.textSecondary,
                                uncheckedTrackColor = AlishaTheme.colors.bgElevated
                            )
                        )
                    }
                }

                // Section 3: Recording Mode
                item {
                    HorizontalDivider(thickness = 0.5.dp, color = AlishaTheme.colors.divider)
                    Spacer(modifier = Modifier.height(20.dp))
                    Text(
                        text = "RECORDING",
                        style = AlishaTheme.typography.labelSmall,
                        color = AlishaTheme.colors.accent
                    )
                    Spacer(modifier = Modifier.height(14.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (isHoldToRecord) "Hold to record" else "Tap to toggle",
                            style = AlishaTheme.typography.conversationText,
                            color = AlishaTheme.colors.textPrimary
                        )
                        Switch(
                            checked = isHoldToRecord,
                            onCheckedChange = { isHoldToRecord = it },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = AlishaTheme.colors.bgBase,
                                checkedTrackColor = AlishaTheme.colors.accent,
                                uncheckedThumbColor = AlishaTheme.colors.textSecondary,
                                uncheckedTrackColor = AlishaTheme.colors.bgElevated
                            )
                        )
                    }
                }

                // Section 4: Advanced Sampling Params (Collapsible)
                item {
                    HorizontalDivider(thickness = 0.5.dp, color = AlishaTheme.colors.divider)
                    Spacer(modifier = Modifier.height(20.dp))
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { isAdvancedExpanded = !isAdvancedExpanded }
                            .padding(vertical = 4.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "ADVANCED PARAMETERS",
                            style = AlishaTheme.typography.labelSmall,
                            color = AlishaTheme.colors.accent
                        )
                        Icon(
                            imageVector = if (isAdvancedExpanded) AlishaIcons.KeyboardArrowUp else AlishaIcons.KeyboardArrowDown,
                            contentDescription = "Expand",
                            tint = AlishaTheme.colors.accent
                        )
                    }

                    AnimatedVisibility(visible = isAdvancedExpanded) {
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 12.dp),
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            Text(
                                text = "Temperature: ${String.format("%.2f", temp)}",
                                style = AlishaTheme.typography.conversationText,
                                color = AlishaTheme.colors.textPrimary
                            )
                            Slider(
                                value = temp,
                                onValueChange = { temp = it },
                                valueRange = 0.3f..1.2f,
                                colors = SliderDefaults.colors(
                                    thumbColor = AlishaTheme.colors.accent,
                                    activeTrackColor = AlishaTheme.colors.accent
                                )
                            )

                            Text(
                                text = "Top-P: ${String.format("%.2f", topP)}",
                                style = AlishaTheme.typography.conversationText,
                                color = AlishaTheme.colors.textPrimary
                            )
                            Slider(
                                value = topP,
                                onValueChange = { topP = it },
                                valueRange = 0.5f..1.0f,
                                colors = SliderDefaults.colors(
                                    thumbColor = AlishaTheme.colors.accent,
                                    activeTrackColor = AlishaTheme.colors.accent
                                )
                            )

                            // Reset Action
                            Box(
                                modifier = Modifier
                                    .clickable {
                                        temp = 0.75f
                                        topP = 0.90f
                                        minP = 0.05f
                                        maxTokens = 60f
                                    }
                                    .padding(vertical = 8.dp)
                            ) {
                                Text(
                                    text = "reset to recommended",
                                    style = AlishaTheme.typography.labelSmall,
                                    color = AlishaTheme.colors.accent
                                )
                            }
                        }
                    }
                }

                // Section 5: Data Management
                item {
                    HorizontalDivider(thickness = 0.5.dp, color = AlishaTheme.colors.divider)
                    Spacer(modifier = Modifier.height(20.dp))
                    Text(
                        text = "DATA",
                        style = AlishaTheme.typography.labelSmall,
                        color = AlishaTheme.colors.accent
                    )
                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                if (isConfirmingClear) {
                                    onClearConversation()
                                    isConfirmingClear = false
                                } else {
                                    isConfirmingClear = true
                                }
                            }
                            .padding(vertical = 10.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = if (isConfirmingClear) "sure? tap again to confirm" else "Clear conversation",
                            style = AlishaTheme.typography.conversationText,
                            color = AlishaTheme.colors.danger
                        )
                    }
                }

                // Footer
                item {
                    Spacer(modifier = Modifier.height(30.dp))
                    Box(
                        modifier = Modifier.fillMaxWidth(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "everything stays on this phone.",
                            style = AlishaTheme.typography.conversationText.copy(fontSize = 13.5.sp),
                            color = AlishaTheme.colors.textSecondary.copy(alpha = 0.6f)
                        )
                    }
                    Spacer(modifier = Modifier.height(40.dp))
                }
            }
        }
    }
}
