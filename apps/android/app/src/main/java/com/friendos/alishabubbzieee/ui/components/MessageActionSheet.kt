package com.friendos.alishabubbzieee.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.shape.RoundedCornerShape
import com.friendos.alishabubbzieee.ui.theme.AlishaIcons
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import com.friendos.alishabubbzieee.ui.theme.AlishaTheme
import kotlinx.coroutines.delay

/**
 * Long-press Action Bottom Sheet.
 * Bottom sheet on bg_elevated, 24dp top radius.
 * Actions: Copy / Save / Delete (with inline "sure?" confirmation).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MessageActionSheet(
    onDismiss: () -> Unit,
    onCopy: () -> Unit,
    onSave: () -> Unit,
    onDelete: () -> Unit
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    var isConfirmingDelete by remember { mutableStateOf(false) }

    LaunchedEffect(isConfirmingDelete) {
        if (isConfirmingDelete) {
            delay(3000)
            isConfirmingDelete = false
        }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = AlishaTheme.colors.bgElevated,
        shape = AlishaTheme.shapes.sheet,
        dragHandle = {
            Box(
                modifier = Modifier
                    .padding(vertical = 12.dp)
                    .width(36.dp)
                    .height(4.dp)
                    .background(AlishaTheme.colors.textSecondary.copy(alpha = 0.4f), RoundedCornerShape(2.dp))
            )
        }
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 8.dp)
                .padding(bottom = 28.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            ActionRow(
                icon = AlishaIcons.ContentCopy,
                label = "Copy",
                onClick = {
                    onCopy()
                    onDismiss()
                }
            )

            ActionRow(
                icon = AlishaIcons.BookmarkBorder,
                label = "Save to memories",
                onClick = {
                    onSave()
                    onDismiss()
                }
            )

            val deleteColor by animateColorAsState(
                targetValue = if (isConfirmingDelete) AlishaTheme.colors.danger else AlishaTheme.colors.textPrimary,
                label = "DeleteColor"
            )

            ActionRow(
                icon = AlishaIcons.DeleteOutline,
                label = if (isConfirmingDelete) "sure?" else "Delete",
                labelColor = deleteColor,
                iconColor = if (isConfirmingDelete) AlishaTheme.colors.danger else AlishaTheme.colors.textSecondary,
                onClick = {
                    if (isConfirmingDelete) {
                        onDelete()
                        onDismiss()
                    } else {
                        isConfirmingDelete = true
                    }
                }
            )
        }
    }
}

@Composable
private fun ActionRow(
    icon: ImageVector,
    label: String,
    onClick: () -> Unit,
    labelColor: androidx.compose.ui.graphics.Color = AlishaTheme.colors.textPrimary,
    iconColor: androidx.compose.ui.graphics.Color = AlishaTheme.colors.textSecondary
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 12.dp, horizontal = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = label,
            tint = iconColor,
            modifier = Modifier.size(20.dp)
        )
        Text(
            text = label,
            style = AlishaTheme.typography.conversationText,
            color = labelColor
        )
    }
}
