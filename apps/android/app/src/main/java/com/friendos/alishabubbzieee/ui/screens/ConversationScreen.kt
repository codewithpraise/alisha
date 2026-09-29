package com.friendos.alishabubbzieee.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
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
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import com.friendos.alishabubbzieee.ui.theme.AlishaIcons
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.unit.dp
import com.friendos.alishabubbzieee.ui.components.BreathingDot
import com.friendos.alishabubbzieee.ui.components.InputBar
import com.friendos.alishabubbzieee.ui.components.MessageActionSheet
import com.friendos.alishabubbzieee.ui.components.MessageBubble
import com.friendos.alishabubbzieee.ui.components.MessageUiModel
import com.friendos.alishabubbzieee.ui.components.TypingIndicator
import com.friendos.alishabubbzieee.ui.theme.AlishaMotion
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

/**
 * Root Conversation Screen.
 * Design Principle: "someone is awake with me at 2am."
 * Warmth over efficiency, intimacy over information density.
 * No top app bar. Minimal status area with breathing presence dot.
 */
@Composable
fun ConversationScreen(
    messages: List<MessageUiModel>,
    isAlishaTyping: Boolean = false,
    activeSpeakingMessageId: String? = null,
    currentSpokenWordIndex: Int = -1,
    onSendMessage: (String) -> Unit,
    onVoiceSend: (Float) -> Unit,
    onOpenCall: () -> Unit,
    onOpenSettings: () -> Unit,
    onDeleteMessage: (String) -> Unit
) {
    var inputText by remember { mutableStateOf("") }
    var isRecording by remember { mutableStateOf(false) }
    var selectedMessageForAction by remember { mutableStateOf<MessageUiModel?>(null) }
    var playingVoiceMessageId by remember { mutableStateOf<String?>(null) }

    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()
    val clipboardManager = LocalClipboardManager.current

    // Auto-scroll when new messages arrive
    LaunchedEffect(messages.size, isAlishaTyping) {
        if (messages.isNotEmpty()) {
            listState.animateScrollToItem(messages.size - 1)
        }
    }

    // Detect if user has scrolled up
    val showScrollToBottom by remember {
        derivedStateOf {
            val totalItems = listState.layoutInfo.totalItemsCount
            val lastVisibleItem = listState.layoutInfo.visibleItemsInfo.lastOrNull()?.index ?: 0
            totalItems > 6 && (totalItems - 1 - lastVisibleItem) > 3
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(AlishaTheme.colors.bgBase)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .statusBarsPadding()
        ) {
            // Minimalist Status Bar Area
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Presence dot + name
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    BreathingDot(
                        dotSize = 5.dp,
                        isBreathing = true
                    )
                    Text(
                        text = "alisha",
                        style = AlishaTheme.typography.titleHumanist,
                        color = AlishaTheme.colors.textPrimary
                    )
                }

                // Ambient Call and Settings entries
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    IconButton(
                        onClick = onOpenCall,
                        modifier = Modifier.size(34.dp)
                    ) {
                        Icon(
                            imageVector = AlishaIcons.Call,
                            contentDescription = "Voice Call",
                            tint = AlishaTheme.colors.textSecondary,
                            modifier = Modifier.size(19.dp)
                        )
                    }

                    IconButton(
                        onClick = onOpenSettings,
                        modifier = Modifier.size(34.dp)
                    ) {
                        Icon(
                            imageVector = AlishaIcons.Settings,
                            contentDescription = "Settings",
                            tint = AlishaTheme.colors.textSecondary,
                            modifier = Modifier.size(19.dp)
                        )
                    }
                }
            }

            // Message Thread or Empty State
            Box(
                modifier = Modifier
                    .weight(1f)
                    .fillMaxWidth()
            ) {
                if (messages.isEmpty() && !isAlishaTyping) {
                    // Empty State: breathing dot pulses center-screen with "hey. i'm here."
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            BreathingDot(
                                dotSize = 8.dp,
                                isBreathing = true
                            )
                            Text(
                                text = "hey. i'm here.",
                                style = AlishaTheme.typography.conversationText,
                                color = AlishaTheme.colors.textSecondary
                            )
                        }
                    }
                } else {
                    LazyColumn(
                        state = listState,
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.spacedBy(2.dp)
                    ) {
                        itemsIndexed(messages, key = { _, item -> item.id }) { index, msg ->
                            val prevMsg = messages.getOrNull(index - 1)
                            val nextMsg = messages.getOrNull(index + 1)

                            val isFirstInBurst = prevMsg?.sender != msg.sender
                            val isLastInBurst = nextMsg?.sender != msg.sender

                            // Floating Timestamp between conversations > 5 mins
                            if (prevMsg != null && (msg.timestampMs - prevMsg.timestampMs > 300_000)) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(vertical = 12.dp),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text(
                                        text = "TODAY",
                                        style = AlishaTheme.typography.timestamp,
                                        color = AlishaTheme.colors.textSecondary
                                    )
                                }
                            }

                            val isThisMsgSpeaking = msg.id == activeSpeakingMessageId

                            MessageBubble(
                                message = msg,
                                isFirstInBurst = isFirstInBurst,
                                isLastInBurst = isLastInBurst,
                                showPresenceDot = isLastInBurst,
                                currentSpokenWordIndex = if (isThisMsgSpeaking) currentSpokenWordIndex else -1,
                                isPlayingVoice = playingVoiceMessageId == msg.id,
                                voicePlayProgress = if (playingVoiceMessageId == msg.id) 0.5f else 0f,
                                onVoicePlayToggle = {
                                    playingVoiceMessageId = if (playingVoiceMessageId == msg.id) null else msg.id
                                },
                                onLongPress = {
                                    selectedMessageForAction = msg
                                }
                            )
                        }

                        if (isAlishaTyping) {
                            item {
                                Box(modifier = Modifier.padding(start = 28.dp, top = 6.dp, bottom = 6.dp)) {
                                    TypingIndicator()
                                }
                            }
                        }
                    }
                }

                // Floating "↓ new" Pill
                if (showScrollToBottom) {
                    Box(
                        modifier = Modifier
                            .align(Alignment.BottomCenter)
                            .padding(bottom = 12.dp)
                            .background(AlishaTheme.colors.bgElevated, RoundedCornerShape(16.dp))
                            .clickable {
                                scope.launch {
                                    if (messages.isNotEmpty()) {
                                        listState.animateScrollToItem(messages.size - 1)
                                    }
                                }
                            }
                            .padding(horizontal = 14.dp, vertical = 6.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = AlishaIcons.KeyboardArrowDown,
                                contentDescription = "Scroll down",
                                tint = AlishaTheme.colors.accent,
                                modifier = Modifier.size(16.dp)
                            )
                            Text(
                                text = "↓ new",
                                style = AlishaTheme.typography.labelSmall,
                                color = AlishaTheme.colors.accent
                            )
                        }
                    }
                }
            }

            // Input Bar (floats above keyboard)
            InputBar(
                modifier = Modifier
                    .fillMaxWidth()
                    .imePadding()
                    .navigationBarsPadding(),
                inputText = inputText,
                onInputTextChange = { inputText = it },
                onSendMessage = onSendMessage,
                onVoiceSend = onVoiceSend,
                isRecording = isRecording,
                onStartRecording = { isRecording = true },
                onStopRecording = { isRecording = false },
                onCancelRecording = { isRecording = false }
            )
        }

        // Long Press Action Sheet
        selectedMessageForAction?.let { msg ->
            MessageActionSheet(
                onDismiss = { selectedMessageForAction = null },
                onCopy = {
                    clipboardManager.setText(AnnotatedString(msg.content))
                },
                onSave = {
                    // Saved to memory bookmarks
                },
                onDelete = {
                    onDeleteMessage(msg.id)
                }
            )
        }
    }
}
