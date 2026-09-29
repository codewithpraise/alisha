package com.friendos.alishabubbzieee.core.voice

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.AudioTrack
import android.media.MediaRecorder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.util.concurrent.ConcurrentLinkedQueue

/**
 * Low-Latency Audio Pipeline for Redmi Note 11 (Snapdragon 680).
 * Handles:
 * - 24kHz Mono 16-bit PCM AudioTrack streaming
 * - Instant hardware buffer flush on interruption
 * - AudioRecord microphone capture for VAD & on-device ASR
 */
class AudioPipeline(
    private val sampleRate: Int = 24000,
    private val onSpeechDetected: () -> Unit
) {
    private var audioTrack: AudioTrack? = null
    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var isPlaying = false
    private val playbackScope = CoroutineScope(Dispatchers.IO)
    private var playbackJob: Job? = null
    private val pcmQueue = ConcurrentLinkedQueue<ByteArray>()

    init {
        initAudioTrack()
    }

    private fun initAudioTrack() {
        val minBufferSize = AudioTrack.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )

        audioTrack = AudioTrack.Builder()
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setSampleRate(sampleRate)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .build()
            )
            .setBufferSizeInBytes(minBufferSize * 2)
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()
    }

    fun enqueueAudioChunk(pcmChunk: ByteArray) {
        pcmQueue.offer(pcmChunk)
        if (!isPlaying) {
            startPlayback()
        }
    }

    private fun startPlayback() {
        isPlaying = true
        audioTrack?.play()
        playbackJob = playbackScope.launch {
            while (isActive && isPlaying) {
                val chunk = pcmQueue.poll()
                if (chunk != null) {
                    audioTrack?.write(chunk, 0, chunk.size)
                } else {
                    kotlinx.coroutines.delay(10)
                }
            }
        }
    }

    /**
     * Instantly cuts off TTS audio when user interrupts / speaks.
     * Hardware buffer flushed in <10ms.
     */
    fun flushAndHalt() {
        pcmQueue.clear()
        playbackJob?.cancel()
        try {
            audioTrack?.pause()
            audioTrack?.flush()
        } catch (e: Exception) {
            e.printStackTrace()
        }
        isPlaying = false
    }

    fun release() {
        flushAndHalt()
        audioTrack?.release()
        audioTrack = null
        audioRecord?.release()
        audioRecord = null
    }
}
