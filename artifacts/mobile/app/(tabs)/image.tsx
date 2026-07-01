import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Platform,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useColors } from "@/hooks/useColors";
import { AsterixHeader } from "@/components/ui/AsterixHeader";
import { GlossyCard } from "@/components/ui/GlossyCard";
import { GoldButton } from "@/components/ui/GoldButton";
import { EmptyState } from "@/components/ui/EmptyState";
import { Typography } from "@/constants/theme";

type ImageAction = "analyze" | "generate" | "edit" | "ocr";

const ACTION_ITEMS: { id: ImageAction; icon: keyof typeof Feather.glyphMap; label: string; description: string }[] = [
  { id: "analyze", icon: "eye", label: "Analyze Image", description: "Describe & understand any image" },
  { id: "generate", icon: "aperture", label: "Generate Image", description: "Create images from text prompts" },
  { id: "edit", icon: "edit-2", label: "Edit Image", description: "Modify and enhance your images" },
  { id: "ocr", icon: "type", label: "Extract Text", description: "Read text from any image (OCR)" },
];

export default function ImageScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;
  const [selectedAction, setSelectedAction] = useState<ImageAction | null>(null);

  function handleAction(id: ImageAction) {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedAction(id);
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <AsterixHeader title="Image AI" />

      <ScrollView
        contentContainerStyle={[
          styles.scroll,
          { paddingBottom: bottomPad + 80 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Text style={[Typography.small, { color: colors.mutedForeground, marginBottom: 16 }]}>
          SELECT ACTION
        </Text>

        {ACTION_ITEMS.map((item) => (
          <TouchableOpacity
            key={item.id}
            onPress={() => handleAction(item.id)}
            activeOpacity={0.8}
          >
            <GlossyCard
              style={[styles.actionCard]}
              goldBorder={selectedAction === item.id}
              bordered={selectedAction !== item.id}
            >
              <View style={styles.actionRow}>
                <View
                  style={[
                    styles.actionIcon,
                    {
                      backgroundColor:
                        selectedAction === item.id ? colors.gold : colors.secondary,
                    },
                  ]}
                >
                  <Feather
                    name={item.icon}
                    size={20}
                    color={
                      selectedAction === item.id
                        ? colors.primaryForeground
                        : colors.mutedForeground
                    }
                  />
                </View>
                <View style={styles.actionText}>
                  <Text style={[Typography.bodyMedium, { color: colors.foreground }]}>
                    {item.label}
                  </Text>
                  <Text style={[Typography.small, { color: colors.mutedForeground }]}>
                    {item.description}
                  </Text>
                </View>
                {selectedAction === item.id && (
                  <Feather name="check-circle" size={18} color={colors.gold} />
                )}
              </View>
            </GlossyCard>
          </TouchableOpacity>
        ))}

        <GlossyCard style={styles.uploadArea} bordered>
          <Feather name="upload" size={32} color={colors.mutedForeground} />
          <Text style={[Typography.bodyMedium, { color: colors.foreground, marginTop: 10 }]}>
            Upload an Image
          </Text>
          <Text style={[Typography.small, { color: colors.mutedForeground, textAlign: "center" }]}>
            Image upload will be available when the backend is connected
          </Text>
        </GlossyCard>

        <GoldButton
          label={selectedAction ? `${ACTION_ITEMS.find((a) => a.id === selectedAction)?.label}` : "Select an action"}
          onPress={() => {}}
          disabled={!selectedAction}
          style={styles.runBtn}
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scroll: { padding: 16, gap: 10 },
  actionCard: { marginBottom: 0 },
  actionRow: { flexDirection: "row", alignItems: "center", gap: 14 },
  actionIcon: {
    width: 44,
    height: 44,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  actionText: { flex: 1 },
  uploadArea: {
    alignItems: "center",
    justifyContent: "center",
    height: 140,
    gap: 8,
    marginTop: 8,
    borderStyle: "dashed",
    borderWidth: 1,
  },
  runBtn: { marginTop: 8 },
});
