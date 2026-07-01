import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useColors } from "@/hooks/useColors";
import { Typography } from "@/constants/theme";

interface EmptyStateProps {
  icon: keyof typeof Ionicons.glyphMap;
  title: string;
  description?: string;
}

export function EmptyState({ icon, title, description }: EmptyStateProps) {
  const colors = useColors();

  return (
    <View style={styles.container}>
      <View style={styles.glowWrap}>
        <View style={[styles.ring3, { borderColor: colors.gold + "18" }]} />
        <View style={[styles.ring2, { borderColor: colors.gold + "30" }]} />
        <View style={[styles.ring1, { borderColor: colors.gold + "55" }]} />
        <View style={[styles.iconCircle, { backgroundColor: colors.secondary }]}>
          <Ionicons name={icon} size={32} color={colors.gold} />
        </View>
      </View>
      <Text style={[Typography.h3, styles.title, { color: colors.foreground }]}>
        {title}
      </Text>
      {description && (
        <Text style={[Typography.body, styles.desc, { color: colors.mutedForeground }]}>
          {description}
        </Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 14,
    paddingHorizontal: 40,
  },
  glowWrap: {
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  ring3: {
    position: "absolute",
    width: 130,
    height: 130,
    borderRadius: 65,
    borderWidth: 1,
  },
  ring2: {
    position: "absolute",
    width: 104,
    height: 104,
    borderRadius: 52,
    borderWidth: 1,
  },
  ring1: {
    position: "absolute",
    width: 82,
    height: 82,
    borderRadius: 41,
    borderWidth: 1,
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: "center",
    justifyContent: "center",
  },
  title: { textAlign: "center" },
  desc: { textAlign: "center", lineHeight: 22 },
});
