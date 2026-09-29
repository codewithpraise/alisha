package com.friendos.alishabubbzieee.ui.theme

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.PathFillType
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.unit.dp

/**
 * Bespoke lightweight Vector Icons for Alisha.
 * Eliminates the need for the heavyweight 60MB material-icons-extended dependency.
 */
object AlishaIcons {
    val ArrowBack: ImageVector = Icons.Default.ArrowBack
    val Check: ImageVector = Icons.Default.Check
    val Close: ImageVector = Icons.Default.Close
    val PlayArrow: ImageVector = Icons.Default.PlayArrow

    val Pause: ImageVector by lazy {
        ImageVector.Builder(
            name = "Pause",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(6f, 19f)
                horizontalLineToRelative(4f)
                verticalLineTo(5f)
                horizontalLineTo(6f)
                verticalLineToRelative(14f)
                close()
                moveTo(14f, 5f)
                verticalLineToRelative(14f)
                horizontalLineToRelative(4f)
                verticalLineTo(5f)
                horizontalLineToRelative(-4f)
                close()
            }
        }.build()
    }

    val ArrowUpward: ImageVector by lazy {
        ImageVector.Builder(
            name = "ArrowUpward",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(4f, 12f)
                lineToRelative(1.41f, 1.41f)
                lineTo(11f, 7.83f)
                verticalLineTo(20f)
                horizontalLineToRelative(2f)
                verticalLineTo(7.83f)
                lineToRelative(5.58f, 5.59f)
                lineTo(20f, 12f)
                lineToRelative(-8f, -8f)
                lineToRelative(-8f, 8f)
                close()
            }
        }.build()
    }

    val Mic: ImageVector by lazy {
        ImageVector.Builder(
            name = "Mic",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(12f, 14f)
                curveToRelative(1.66f, 0f, 3f, -1.34f, 3f, -3f)
                verticalLineTo(5f)
                curveToRelative(0f, -1.66f, -1.34f, -3f, -3f, -3f)
                reflectiveCurveTo(9f, 3.34f, 9f, 5f)
                verticalLineToRelative(6f)
                curveToRelative(0f, 1.66f, 1.34f, 3f, 3f, 3f)
                close()
                moveTo(17f, 11f)
                curveToRelative(0f, 2.76f, -2.24f, 5f, -5f, 5f)
                reflectiveCurveToRelative(-5f, -2.24f, -5f, -5f)
                horizontalLineTo(5f)
                curveToRelative(0f, 3.53f, 2.61f, 6.43f, 6f, 6.92f)
                verticalLineTo(21f)
                horizontalLineToRelative(2f)
                verticalLineToRelative(-3.08f)
                curveToRelative(3.39f, -0.49f, 6f, -3.39f, 6f, -6.92f)
                horizontalLineToRelative(-2f)
                close()
            }
        }.build()
    }

    val MicOff: ImageVector by lazy {
        ImageVector.Builder(
            name = "MicOff",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(19f, 11f)
                horizontalLineToRelative(-1.7f)
                curveToRelative(0f, 0.74f, -0.16f, 1.43f, -0.43f, 2.05f)
                lineToRelative(1.23f, 1.23f)
                curveToRelative(0.56f, -0.98f, 0.9f, -2.09f, 0.9f, -3.28f)
                close()
                moveTo(14.85f, 14.85f)
                lineTo(4.41f, 4.41f)
                lineTo(3f, 5.82f)
                lineToRelative(6.13f, 6.13f)
                verticalLineTo(11f)
                curveToRelative(0f, 1.66f, 1.34f, 3f, 3f, 3f)
                curveToRelative(0.33f, 0f, 0.65f, -0.06f, 0.95f, -0.16f)
                lineToRelative(2.32f, 2.32f)
                curveTo(14.07f, 16.63f, 12.59f, 17f, 11f, 17f)
                curveToRelative(-3.53f, 0f, -6f, -2.89f, -6f, -6f)
                horizontalLineTo(3.3f)
                curveToRelative(0f, 3.84f, 2.82f, 7f, 6.7f, 7.55f)
                verticalLineTo(21f)
                horizontalLineToRelative(2f)
                verticalLineToRelative(-2.45f)
                curveToRelative(1.5f, -0.21f, 2.89f, -0.84f, 4.05f, -1.74f)
                lineToRelative(2.13f, 2.13f)
                lineToRelative(1.41f, -1.41f)
                lineToRelative(-4.74f, -4.68f)
                close()
            }
        }.build()
    }

    val Stop: ImageVector by lazy {
        ImageVector.Builder(
            name = "Stop",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(6f, 6f)
                horizontalLineToRelative(12f)
                verticalLineToRelative(12f)
                horizontalLineTo(6f)
                close()
            }
        }.build()
    }

    val Call: ImageVector by lazy {
        ImageVector.Builder(
            name = "Call",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(20.01f, 15.38f)
                curveToRelative(-1.23f, 0f, -2.42f, -0.2f, -3.53f, -0.56f)
                curveToRelative(-0.35f, -0.12f, -0.74f, -0.03f, -1.02f, 0.24f)
                lineToRelative(-2.2f, 2.2f)
                curveToRelative(-2.83f, -1.44f, -5.15f, -3.75f, -6.59f, -6.59f)
                lineToRelative(2.2f, -2.21f)
                curveToRelative(0.28f, -0.27f, 0.36f, -0.66f, 0.25f, -1.01f)
                curveTo(8.7f, 6.45f, 8.5f, 5.25f, 8.5f, 4.01f)
                curveToRelative(0f, -0.55f, -0.45f, -1f, -1f, -1f)
                horizontalLineTo(4f)
                curveToRelative(-0.55f, 0f, -1f, 0.45f, -1f, 1f)
                curveToRelative(0f, 9.39f, 7.61f, 17f, 17f, 17f)
                curveToRelative(0.55f, 0f, 1f, -0.45f, 1f, -1f)
                verticalLineToRelative(-3.5f)
                curveToRelative(0f, -0.55f, -0.45f, -1f, -1f, -1f)
                close()
            }
        }.build()
    }

    val CallEnd: ImageVector by lazy {
        ImageVector.Builder(
            name = "CallEnd",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(12f, 9f)
                curveToRelative(-1.6f, 0f, -3.15f, 0.25f, -4.6f, 0.72f)
                verticalLineToRelative(3.1f)
                curveToRelative(0f, 0.39f, -0.23f, 0.74f, -0.56f, 0.9f)
                curveToRelative(-0.98f, 0.49f, -1.87f, 1.12f, -2.66f, 1.85f)
                curveToRelative(-0.18f, 0.18f, -0.43f, 0.28f, -0.7f, 0.28f)
                curveToRelative(-0.28f, 0f, -0.53f, -0.11f, -0.71f, -0.29f)
                lineTo(0.29f, 13.08f)
                curveToRelative(-0.18f, -0.17f, -0.29f, -0.42f, -0.29f, -0.7f)
                curveToRelative(0f, -0.28f, 0.11f, -0.53f, 0.29f, -0.71f)
                curveTo(3.34f, 8.78f, 7.46f, 7f, 12f, 7f)
                reflectiveCurveToRelative(8.66f, 1.78f, 11.71f, 4.67f)
                curveToRelative(0.18f, 0.18f, 0.29f, 0.43f, 0.29f, 0.71f)
                curveToRelative(0f, 0.28f, -0.11f, 0.53f, -0.29f, 0.71f)
                lineToRelative(-2.48f, 2.48f)
                curveToRelative(-0.18f, 0.18f, -0.43f, 0.29f, -0.71f, 0.29f)
                curveToRelative(-0.27f, 0f, -0.52f, -0.11f, -0.7f, -0.28f)
                curveToRelative(-0.79f, -0.74f, -1.69f, -1.36f, -2.67f, -1.85f)
                curveToRelative(-0.33f, -0.16f, -0.56f, -0.5f, -0.56f, -0.9f)
                verticalLineToRelative(-3.1f)
                curveTo(15.15f, 9.25f, 13.6f, 9f, 12f, 9f)
                close()
            }
        }.build()
    }

    val VolumeUp: ImageVector by lazy {
        ImageVector.Builder(
            name = "VolumeUp",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(3f, 9f)
                verticalLineToRelative(6f)
                horizontalLineToRelative(4f)
                lineToRelative(5f, 5f)
                verticalLineTo(4f)
                lineTo(7f, 9f)
                horizontalLineTo(3f)
                close()
                moveTo(16.5f, 12f)
                curveToRelative(0f, -1.77f, -1.02f, -3.29f, -2.5f, -4.03f)
                verticalLineToRelative(8.05f)
                curveToRelative(1.48f, -0.73f, 2.5f, -2.25f, 2.5f, -4.02f)
                close()
                moveTo(14f, 3.23f)
                verticalLineToRelative(2.06f)
                curveToRelative(2.89f, 0.86f, 5f, 3.54f, 5f, 6.71f)
                reflectiveCurveToRelative(-2.11f, 5.85f, -5f, 6.71f)
                verticalLineToRelative(2.06f)
                curveToRelative(4.01f, -0.91f, 7f, -4.49f, 7f, -8.77f)
                reflectiveCurveToRelative(-2.99f, -7.86f, -7f, -8.77f)
                close()
            }
        }.build()
    }

    val Settings: ImageVector by lazy {
        ImageVector.Builder(
            name = "Settings",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(19.14f, 12.94f)
                curveToRelative(0.04f, -0.3f, 0.06f, -0.61f, 0.06f, -0.94f)
                reflectiveCurveToRelative(-0.02f, -0.64f, -0.07f, -0.94f)
                lineToRelative(2.03f, -1.58f)
                curveToRelative(0.18f, -0.14f, 0.23f, -0.41f, 0.12f, -0.61f)
                lineToRelative(-1.92f, -3.32f)
                curveToRelative(-0.12f, -0.22f, -0.37f, -0.29f, -0.59f, -0.22f)
                lineToRelative(-2.39f, 0.96f)
                curveToRelative(-0.5f, -0.38f, -1.03f, -0.7f, -1.62f, -0.94f)
                lineToRelative(-0.36f, -2.54f)
                curveToRelative(-0.04f, -0.24f, -0.24f, -0.41f, -0.48f, -0.41f)
                horizontalLineToRelative(-3.84f)
                curveToRelative(-0.24f, 0f, -0.43f, 0.17f, -0.47f, 0.41f)
                lineToRelative(-0.36f, 2.54f)
                curveToRelative(-0.59f, 0.24f, -1.13f, 0.57f, -1.62f, 0.94f)
                lineToRelative(-2.39f, -0.96f)
                curveToRelative(-0.22f, -0.08f, -0.47f, 0f, -0.59f, 0.22f)
                lineTo(2.74f, 8.87f)
                curveToRelative(-0.12f, 0.21f, -0.08f, 0.47f, 0.12f, 0.61f)
                lineToRelative(2.03f, 1.58f)
                curveToRelative(-0.05f, 0.3f, -0.09f, 0.63f, -0.09f, 0.94f)
                reflectiveCurveToRelative(0.02f, 0.64f, 0.07f, 0.94f)
                lineToRelative(-2.03f, 1.58f)
                curveToRelative(-0.18f, 0.14f, -0.23f, 0.41f, -0.12f, 0.61f)
                lineToRelative(1.92f, 3.32f)
                curveToRelative(0.12f, 0.22f, 0.37f, 0.29f, 0.59f, 0.22f)
                lineToRelative(2.39f, -0.96f)
                curveToRelative(0.5f, 0.38f, 1.03f, 0.7f, 1.62f, 0.94f)
                lineToRelative(0.36f, 2.54f)
                curveToRelative(0.05f, 0.24f, 0.24f, 0.41f, 0.48f, 0.41f)
                horizontalLineToRelative(3.84f)
                curveToRelative(0.24f, 0f, 0.44f, -0.17f, 0.47f, -0.41f)
                lineToRelative(0.36f, -2.54f)
                curveToRelative(0.59f, -0.24f, 1.13f, -0.56f, 1.62f, -0.94f)
                lineToRelative(2.39f, 0.96f)
                curveToRelative(0.22f, 0.08f, 0.47f, 0f, 0.59f, -0.22f)
                lineToRelative(1.92f, -3.32f)
                curveToRelative(0.12f, -0.22f, 0.07f, -0.47f, -0.12f, -0.61f)
                lineToRelative(-2.01f, -1.58f)
                close()
                moveTo(12f, 15.6f)
                curveToRelative(-1.98f, 0f, -3.6f, -1.62f, -3.6f, -3.6f)
                reflectiveCurveToRelative(1.62f, -3.6f, 3.6f, -3.6f)
                reflectiveCurveToRelative(3.6f, 1.62f, 3.6f, 3.6f)
                reflectiveCurveToRelative(-1.62f, 3.6f, -3.6f, 3.6f)
                close()
            }
        }.build()
    }

    val KeyboardArrowDown: ImageVector by lazy {
        ImageVector.Builder(
            name = "KeyboardArrowDown",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(7.41f, 8.59f)
                lineTo(12f, 13.17f)
                lineToRelative(4.59f, -4.58f)
                lineTo(18f, 10f)
                lineToRelative(-6f, 6f)
                lineToRelative(-6f, -6f)
                lineToRelative(1.41f, -1.41f)
                close()
            }
        }.build()
    }

    val KeyboardArrowUp: ImageVector by lazy {
        ImageVector.Builder(
            name = "KeyboardArrowUp",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(7.41f, 15.41f)
                lineTo(12f, 10.83f)
                lineToRelative(4.59f, 4.58f)
                lineTo(18f, 14f)
                lineToRelative(-6f, -6f)
                lineToRelative(-6f, 6f)
                lineToRelative(1.41f, 1.41f)
                close()
            }
        }.build()
    }

    val ContentCopy: ImageVector by lazy {
        ImageVector.Builder(
            name = "ContentCopy",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(16f, 1f)
                horizontalLineTo(4f)
                curveToRelative(-1.1f, 0f, -2f, 0.9f, -2f, 2f)
                verticalLineToRelative(14f)
                horizontalLineToRelative(2f)
                verticalLineTo(3f)
                horizontalLineToRelative(12f)
                verticalLineTo(1f)
                close()
                moveTo(19f, 5f)
                horizontalLineTo(8f)
                curveToRelative(-1.1f, 0f, -2f, 0.9f, -2f, 2f)
                verticalLineToRelative(14f)
                curveToRelative(0f, 1.1f, 0.9f, 2f, 2f, 2f)
                horizontalLineToRelative(11f)
                curveToRelative(1.1f, 0f, 2f, -0.9f, 2f, -2f)
                verticalLineTo(7f)
                curveToRelative(0f, -1.1f, -0.9f, -2f, -2f, -2f)
                close()
                moveTo(19f, 21f)
                horizontalLineTo(8f)
                verticalLineTo(7f)
                horizontalLineToRelative(11f)
                verticalLineToRelative(14f)
                close()
            }
        }.build()
    }

    val BookmarkBorder: ImageVector by lazy {
        ImageVector.Builder(
            name = "BookmarkBorder",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(17f, 3f)
                horizontalLineTo(7f)
                curveToRelative(-1.1f, 0f, -2f, 0.9f, -2f, 2f)
                verticalLineToRelative(16f)
                lineToRelative(7f, -3f)
                lineToRelative(7f, 3f)
                verticalLineTo(5f)
                curveToRelative(0f, -1.1f, -0.9f, -2f, -2f, -2f)
                close()
                moveTo(17f, 18f)
                lineToRelative(-5f, -2.18f)
                lineTo(7f, 18f)
                verticalLineTo(5f)
                horizontalLineToRelative(10f)
                verticalLineToRelative(13f)
                close()
            }
        }.build()
    }

    val DeleteOutline: ImageVector by lazy {
        ImageVector.Builder(
            name = "DeleteOutline",
            defaultWidth = 24.dp,
            defaultHeight = 24.dp,
            viewportWidth = 24f,
            viewportHeight = 24f
        ).apply {
            path(fill = SolidColor(Color.White)) {
                moveTo(6f, 19f)
                curveToRelative(0f, 1.1f, 0.9f, 2f, 2f, 2f)
                horizontalLineToRelative(8f)
                curveToRelative(1.1f, 0f, 2f, -0.9f, 2f, -2f)
                verticalLineTo(7f)
                horizontalLineTo(6f)
                verticalLineToRelative(12f)
                close()
                moveTo(8f, 9f)
                horizontalLineToRelative(8f)
                verticalLineToRelative(10f)
                horizontalLineTo(8f)
                verticalLineTo(9f)
                close()
                moveTo(15.5f, 4f)
                lineToRelative(-1f, -1f)
                horizontalLineToRelative(-5f)
                lineToRelative(-1f, 1f)
                horizontalLineTo(5f)
                verticalLineToRelative(2f)
                horizontalLineToRelative(14f)
                verticalLineTo(4f)
                horizontalLineToRelative(-3.5f)
                close()
            }
        }.build()
    }
}
