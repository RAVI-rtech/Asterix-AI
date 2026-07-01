import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Platform,
} from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  Easing,
} from "react-native-reanimated";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useColors } from "@/hooks/useColors";
import { AsterixHeader } from "@/components/ui/AsterixHeader";
import { GlossyCard } from "@/components/ui/GlossyCard";
import { Typography } from "@/constants/theme";

type VoiceState = "idle" | "listening" | "processing";

export default function VoiceScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;
  const [voiceState, setVoiceState] = useState<VoiceState>("idle");
  const [transcript, setTranscript] = useState<string>("");

  const pulseScale = useSharedValue(1);

  function startListening() {
    setVoiceState("listening");
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    pulseScale.value = withRepeat(
      withTiming(1.18, { duration: 800, easing: Easing.inOut(Easing.ease) }),
      -1,
      true
    );
    setTimeout(() => {
      setTranscript("Voice recognition will be available in the next phase.");
      stopListening();
    }, 3000);
  }

  function stopListening() {
    setVoiceState("processing");
    pulseScale.value = withTiming(1);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    setTimeout(() => setVoiceState("idle"), 1000);
  }

  function handleMicPress() {
    if (voiceState === "idle") startListening();
    else stopListening();
  }

  const pulseStyle = useAnimatedStyle(() => ({
    transform: [{ scale: pulseScale.value }],
  }));

  const stateLabel =
    voiceState === "idle"
      ? "Tap to speak"
      : voiceState === "listening"
      ? "Listening..."
      : "Processing...";

  const isListening = voiceState === "listening";

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <AsterixHeader title="Voice" />

      <View style={[styles.body, { paddingBottom: bottomPad + 80 }]}>
        <Animated.View style={[styles.pulseRing, pulseStyle]}>
          <View style={[styles.ring3, { borderColor: colors.gold + "20" }]} />
          <View style={[styles.ring2, { borderColor: colors.gold + "40" }]} />
          <View
            style={[
              styles.pulseRingInner,
              { borderColor: isListening ? colors.gold : colors.border },
            ]}
          />
        </Animated.View>

        <TouchableOpacity
          onPress={handleMicPress}
          style={[
            styles.micButton,
            {
              backgroundColor: isListening ? colors.gold : colors.secondary,
              shadowColor: colors.gold,
              shadowOpacity: isListening ? 0.45 : 0,
              shadowRadius: 20,
              elevation: isListening ? 10 : 0,
            },
          ]}
        >
          <Ionicons
            name={isListening ? "mic" : "mic-outline"}
            size={38}
            color={isListening ? colors.primaryForeground : colors.mutedForeground}
          />
        </TouchableOpacity>

        <Text style={[Typography.bodyMedium, { color: colors.mutedForeground, marginTop: 20 }]}>
          {stateLabel}
        </Text>

        {transcript !== "" && (
          <GlossyCard style={styles.transcriptCard} bordered>
            <Text style={[Typography.label, { color: colors.gold, marginBottom: 8 }]}>
              TRANSCRIPT
            </Text>
            <Text style={[Typography.body, { color: colors.foreground }]}>
              {transcript}
            </Text>
          </GlossyCard>
        )}

        <GlossyCard style={styles.infoCard} goldBorder>
          <View style={styles.infoRow}>
            <Ionicons name="sparkles-outline" size={16} color={colors.gold} />
            <Text style={[Typography.label, { color: colors.gold }]}>VOICE MODULE</Text>
          </View>
          <Text style={[Typography.small, { color: colors.mutedForeground, lineHeight: 18, marginTop: 8 }]}>
            Speech-to-text recognition, text-to-speech synthesis, and wake-word detection
            will be enabled when AI features are wired to the backend.
          </Text>
        </GlossyCard>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  body: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
    gap: 16,
  },
  pulseRing: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
  ring3: {
    position: "absolute",
    width: 190,
    height: 190,
    borderRadius: 95,
    borderWidth: 1,
  },
  ring2: {
    position: "absolute",
    width: 150,
    height: 150,
    borderRadius: 75,
    borderWidth: 1,
  },
  pulseRingInner: {
    width: 118,
    height: 118,
    borderRadius: 59,
    borderWidth: 1.5,
  },
  micButton: {
    width: 96,
    height: 96,
    borderRadius: 48,
    alignItems: "center",
    justifyContent: "center",
  },
  transcriptCard: { width: "100%", marginTop: 8 },
  infoCard: { width: "100%", marginTop: 8 },
  infoRow: { flexDirection: "row", alignItems: "center", gap: 8 },
});
