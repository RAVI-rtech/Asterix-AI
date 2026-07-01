import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Platform,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useColors } from "@/hooks/useColors";
import { useSettings, AIModel } from "@/contexts/SettingsContext";
import { useAuth } from "@/contexts/AuthContext";
import { AsterixHeader } from "@/components/ui/AsterixHeader";
import { GlossyCard } from "@/components/ui/GlossyCard";
import { GoldButton } from "@/components/ui/GoldButton";
import { Typography } from "@/constants/theme";

const MODELS: { id: AIModel; label: string; description: string }[] = [
  { id: "gpt-4o", label: "AstraMind AI", description: "Most capable · Recommended" },
  { id: "gpt-4o-mini", label: "AstraMind AI Mini", description: "Fast & efficient" },
  { id: "claude-3-5-sonnet", label: "AstraMind AI 3.5", description: "Excellent reasoning" },
  { id: "gemini-pro", label: "AstraMind AI Pro", description: "Our's best model" },
];

function SectionTitle({ label }: { label: string }) {
  const colors = useColors();
  return (
    <Text style={[Typography.label, { color: colors.gold, marginBottom: 8, marginTop: 16 }]}>
      {label}
    </Text>
  );
}

function SettingRow({
  icon,
  label,
  value,
  onPress,
  rightElement,
}: {
  icon: keyof typeof Feather.glyphMap;
  label: string;
  value?: string;
  onPress?: () => void;
  rightElement?: React.ReactNode;
}) {
  const colors = useColors();
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.7} disabled={!onPress}>
      <View style={[styles.settingRow, { borderBottomColor: colors.border }]}>
        <Feather name={icon} size={18} color={colors.mutedForeground} />
        <Text style={[Typography.bodyMedium, styles.settingLabel, { color: colors.foreground }]}>
          {label}
        </Text>
        {value && (
          <Text style={[Typography.small, { color: colors.mutedForeground }]}>{value}</Text>
        )}
        {rightElement}
        {onPress && <Feather name="chevron-right" size={16} color={colors.mutedForeground} />}
      </View>
    </TouchableOpacity>
  );
}

export default function SettingsScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;
  const { settings, updateSetting, resetSettings } = useSettings();
  const { user, logout } = useAuth();

  function toggleSwitch(key: "voiceEnabled" | "hapticFeedback" | "streamingEnabled" | "autoSaveChats") {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    updateSetting(key, !settings[key]);
  }

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <AsterixHeader title="Settings" />

      <ScrollView
        contentContainerStyle={[styles.scroll, { paddingBottom: bottomPad + 80 }]}
        showsVerticalScrollIndicator={false}
      >
        {user && (
          <GlossyCard goldBorder style={styles.profileCard}>
            <View style={[styles.avatar, { backgroundColor: colors.gold }]}>
              <Text style={[Typography.h2, { color: colors.primaryForeground }]}>
                {user.name[0].toUpperCase()}
              </Text>
            </View>
            <View>
              <Text style={[Typography.h3, { color: colors.foreground }]}>{user.name}</Text>
              <Text style={[Typography.small, { color: colors.mutedForeground }]}>
                {user.email}
              </Text>
              <View style={[styles.badge, { backgroundColor: colors.secondary }]}>
                <Text style={[Typography.caption, { color: colors.gold }]}>FREE TIER</Text>
              </View>
            </View>
          </GlossyCard>
        )}

        <SectionTitle label="AI MODEL" />
        <GlossyCard bordered>
          {MODELS.map((model, i) => (
            <TouchableOpacity
              key={model.id}
              onPress={() => updateSetting("selectedModel", model.id)}
              style={[
                styles.modelRow,
                i < MODELS.length - 1 && { borderBottomWidth: 0.5, borderBottomColor: colors.border },
              ]}
            >
              <View style={styles.modelText}>
                <Text style={[Typography.bodyMedium, { color: colors.foreground }]}>
                  {model.label}
                </Text>
                <Text style={[Typography.small, { color: colors.mutedForeground }]}>
                  {model.description}
                </Text>
              </View>
              {settings.selectedModel === model.id && (
                <Feather name="check" size={18} color={colors.gold} />
              )}
            </TouchableOpacity>
          ))}
        </GlossyCard>

        <SectionTitle label="PREFERENCES" />
        <GlossyCard bordered>
          <SettingRow
            icon="mic"
            label="Voice Input"
            rightElement={
              <Switch
                value={settings.voiceEnabled}
                onValueChange={() => toggleSwitch("voiceEnabled")}
                trackColor={{ false: colors.border, true: colors.gold }}
                thumbColor={colors.foreground}
              />
            }
          />
          <SettingRow
            icon="zap"
            label="Haptic Feedback"
            rightElement={
              <Switch
                value={settings.hapticFeedback}
                onValueChange={() => toggleSwitch("hapticFeedback")}
                trackColor={{ false: colors.border, true: colors.gold }}
                thumbColor={colors.foreground}
              />
            }
          />
          <SettingRow
            icon="activity"
            label="Streaming Responses"
            rightElement={
              <Switch
                value={settings.streamingEnabled}
                onValueChange={() => toggleSwitch("streamingEnabled")}
                trackColor={{ false: colors.border, true: colors.gold }}
                thumbColor={colors.foreground}
              />
            }
          />
          <SettingRow
            icon="save"
            label="Auto-save Chats"
            rightElement={
              <Switch
                value={settings.autoSaveChats}
                onValueChange={() => toggleSwitch("autoSaveChats")}
                trackColor={{ false: colors.border, true: colors.gold }}
                thumbColor={colors.foreground}
              />
            }
          />
        </GlossyCard>

        <SectionTitle label="ABOUT" />
        <GlossyCard bordered>
          <SettingRow icon="star" label="Version" value="1.0.0" />
          <SettingRow icon="shield" label="Privacy Policy" onPress={() => {}} />
          <SettingRow icon="file-text" label="Terms of Service" onPress={() => {}} />
        </GlossyCard>

        <GoldButton
          label="Reset All Settings"
          onPress={resetSettings}
          variant="outline"
          style={{ marginTop: 16 }}
        />

        {user && (
          <GoldButton
            label="Sign Out"
            onPress={logout}
            variant="ghost"
            style={{ marginTop: 8 }}
            textStyle={{ color: colors.destructive }}
          />
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  scroll: { padding: 16 },
  profileCard: { flexDirection: "row", alignItems: "center", gap: 16, marginBottom: 0 },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: "center",
    justifyContent: "center",
  },
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginTop: 4,
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    paddingVertical: 12,
    borderBottomWidth: 0.5,
  },
  settingLabel: { flex: 1 },
  modelRow: { flexDirection: "row", alignItems: "center", paddingVertical: 12 },
  modelText: { flex: 1 },
});
