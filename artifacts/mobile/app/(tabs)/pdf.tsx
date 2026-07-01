import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  TextInput,
  Platform,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useColors } from "@/hooks/useColors";
import { AsterixHeader } from "@/components/ui/AsterixHeader";
import { GlossyCard } from "@/components/ui/GlossyCard";
import { GoldButton } from "@/components/ui/GoldButton";
import { Typography } from "@/constants/theme";

type PDFAction = "summarize" | "qa" | "extract" | "translate";

const PDF_ACTIONS: { id: PDFAction; icon: keyof typeof Ionicons.glyphMap; label: string }[] = [
  { id: "summarize", icon: "list-outline", label: "Summarize" },
  { id: "qa", icon: "help-circle-outline", label: "Q&A" },
  { id: "extract", icon: "cut-outline", label: "Extract Data" },
  { id: "translate", icon: "globe-outline", label: "Translate" },
];

interface MockDocument {
  id: string;
  name: string;
  pages: number;
  size: string;
}

export default function PDFScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;
  const [selectedAction, setSelectedAction] = useState<PDFAction>("summarize");
  const [question, setQuestion] = useState<string>("");
  const [documents] = useState<MockDocument[]>([]);

  function handleSelectAction(id: PDFAction) {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSelectedAction(id);
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <AsterixHeader title="PDF AI" />

      <ScrollView
        contentContainerStyle={[styles.scroll, { paddingBottom: bottomPad + 80 }]}
        showsVerticalScrollIndicator={false}
      >
        {documents.length === 0 ? (
          <GlossyCard style={styles.uploadCard} bordered>
            <View style={[styles.iconWrap, { backgroundColor: colors.secondary }]}>
              <Ionicons name="document-attach-outline" size={34} color={colors.gold} />
            </View>
            <Text style={[Typography.h3, { color: colors.foreground, marginTop: 14 }]}>
              No Documents
            </Text>
            <Text
              style={[
                Typography.small,
                { color: colors.mutedForeground, textAlign: "center", marginTop: 6 },
              ]}
            >
              Upload a PDF to start analyzing it with AI
            </Text>
            <GoldButton
              label="Upload PDF"
              onPress={() => {}}
              style={{ marginTop: 16 }}
              size="sm"
            />
          </GlossyCard>
        ) : (
          documents.map((doc) => (
            <GlossyCard key={doc.id} bordered style={styles.docCard}>
              <View style={styles.docRow}>
                <Ionicons name="document-text" size={28} color={colors.gold} />
                <View style={styles.docInfo}>
                  <Text style={[Typography.bodyMedium, { color: colors.foreground }]}>
                    {doc.name}
                  </Text>
                  <Text style={[Typography.small, { color: colors.mutedForeground }]}>
                    {doc.pages} pages · {doc.size}
                  </Text>
                </View>
                <TouchableOpacity>
                  <Ionicons name="trash-outline" size={18} color={colors.destructive} />
                </TouchableOpacity>
              </View>
            </GlossyCard>
          ))
        )}

        <Text style={[Typography.label, { color: colors.gold, marginTop: 16, marginBottom: 8 }]}>
          ACTION
        </Text>
        <View style={styles.actionsRow}>
          {PDF_ACTIONS.map((action) => (
            <TouchableOpacity
              key={action.id}
              onPress={() => handleSelectAction(action.id)}
              style={[
                styles.actionChip,
                {
                  backgroundColor:
                    selectedAction === action.id ? colors.gold : colors.secondary,
                  borderColor: selectedAction === action.id ? colors.gold : colors.border,
                },
              ]}
            >
              <Ionicons
                name={action.icon}
                size={14}
                color={
                  selectedAction === action.id
                    ? colors.primaryForeground
                    : colors.mutedForeground
                }
              />
              <Text
                style={[
                  Typography.smallMedium,
                  {
                    color:
                      selectedAction === action.id
                        ? colors.primaryForeground
                        : colors.mutedForeground,
                  },
                ]}
              >
                {action.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {selectedAction === "qa" && (
          <View
            style={[
              styles.questionInput,
              { backgroundColor: colors.card, borderColor: colors.border },
            ]}
          >
            <TextInput
              style={[
                Typography.body,
                { color: colors.foreground, fontFamily: "Inter_400Regular" },
              ]}
              placeholder="Ask a question about the document..."
              placeholderTextColor={colors.mutedForeground}
              value={question}
              onChangeText={setQuestion}
              multiline
            />
          </View>
        )}

        <GlossyCard style={styles.infoCard} goldBorder>
          <View style={styles.infoRow}>
            <Ionicons name="sparkles-outline" size={16} color={colors.gold} />
            <Text style={[Typography.label, { color: colors.gold }]}>PDF MODULE</Text>
          </View>
          <Text style={[Typography.small, { color: colors.mutedForeground, lineHeight: 18, marginTop: 8 }]}>
            Full PDF parsing, vector embedding, and semantic search will be enabled
            when the FastAPI backend is connected.
          </Text>
        </GlossyCard>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scroll: { padding: 16, gap: 10 },
  uploadCard: {
    alignItems: "center",
    paddingVertical: 36,
    marginBottom: 8,
  },
  iconWrap: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: "center",
    justifyContent: "center",
  },
  docCard: { marginBottom: 0 },
  docRow: { flexDirection: "row", alignItems: "center", gap: 12 },
  docInfo: { flex: 1 },
  actionsRow: { flexDirection: "row", gap: 8, flexWrap: "wrap" },
  actionChip: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 0.5,
  },
  questionInput: {
    borderRadius: 12,
    borderWidth: 0.5,
    padding: 14,
    minHeight: 80,
    marginTop: 8,
  },
  infoCard: { marginTop: 8 },
  infoRow: { flexDirection: "row", alignItems: "center", gap: 8 },
});
