package com.astramind.presentation.voice

import android.content.Context
import android.speech.SpeechRecognizer
import kotlinx.coroutines.flow.MutableStateFlow

class VoiceManager(private val context: Context) {
    private val _isListening = MutableStateFlow(false)
    val isListening = _isListening

    fun startListening() {
        // Logic for integrating Android SpeechRecognizer or Whisper streaming
        _isListening.value = true
    }

    fun stopListening() {
        _isListening.value = false
    }
}