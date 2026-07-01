package com.astramind.presentation.study

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun StudyScreen() {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        Text("Study Companion", style = MaterialTheme.typography.titleLarge)
        // Flashcards, Document Summarizer, Math Solver modules
    }
}