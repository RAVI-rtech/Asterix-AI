package com.astramind.presentation.vision

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

val PremiumBlack = Color(0xFF0A0A0A)
val GlossyGold = Color(0xFFD4AF37)

@Composable
fun VisionScreen(viewModel: VisionViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(PremiumBlack)
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Vision AI", style = MaterialTheme.typography.headlineMedium, color = GlossyGold)
        
        Spacer(modifier = Modifier.height(32.dp))

        // Image Preview Placeholder
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(250.dp)
                .background(Color(0xFF1C1C1C), RoundedCornerShape(16.dp)),
            contentAlignment = Alignment.Center
        ) {
            Text("Capture or Upload Image", color = Color.Gray)
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Action Buttons
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            Button(onClick = { /* Launch Camera */ }, colors = ButtonDefaults.buttonColors(containerColor = GlossyGold)) {
                Icon(Icons.Default.CameraAlt, contentDescription = null, tint = PremiumBlack)
                Spacer(Modifier.width(8.dp))
                Text("Camera", color = PremiumBlack)
            }
            
            OutlinedButton(onClick = { /* Launch Gallery */ }, colors = ButtonDefaults.outlinedButtonColors(contentColor = GlossyGold)) {
                Icon(Icons.Default.Image, contentDescription = null)
                Spacer(Modifier.width(8.dp))
                Text("Gallery")
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        if (uiState.isLoading) {
            CircularProgressIndicator(color = GlossyGold)
        } else if (uiState.result != null) {
            Text(uiState.result!!, color = Color.White, modifier = Modifier.padding(16.dp))
        }
    }
}