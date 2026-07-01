import React, { useRef, useEffect } from "react";
import {
  View,
  FlatList,
  Text,
  TouchableOpacity,
  StyleSheet,
  Platform,
} from "react-native";
import { KeyboardAvoidingView } from "react-native-keyboard-controller";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Feather } from "@expo/vector-icons";

import { useChat } from "@/contexts/ChatContext";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { ChatInput } from "@/components/chat/ChatInput";
import { AsterixHeader } from "@/components/ui/AsterixHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { useColors } from "@/hooks/useColors";
import { Typography } from "@/constants/theme";

export default function ChatScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { activeConversation, createConversation, sendMessage, isTyping } = useChat();
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    if (!activeConversation) {
      createConversation();
    }
  }, []);

  function handleSend(text: string) {
    sendMessage(text);
  }

  const messages = activeConversation?.messages ?? [];

  return (
    <View style={[styles.container, { backgroundColor: colors.background }]}>
      <AsterixHeader
        showLogo
        rightAction={{
          icon: "plus-square",
          onPress: () => createConversation(),
        }}
      />

      <KeyboardAvoidingView
        style={styles.flex}
        behavior="padding"
        keyboardVerticalOffset={0}
      >
        {messages.length === 0 ? (
          <View style={styles.flex}>
            <EmptyState
              icon="chatbubble-ellipses-outline"
              title="Start a conversation"
              description="Ask anything — Asterix AI is ready to help you."
            />
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => <ChatBubble message={item} />}
            contentContainerStyle={[
              styles.list,
              { paddingBottom: Platform.OS === "web" ? 34 : insets.bottom + 16 },
            ]}
            onContentSizeChange={() =>
              flatListRef.current?.scrollToEnd({ animated: true })
            }
            showsVerticalScrollIndicator={false}
          />
        )}

        {isTyping && (
          <View style={[styles.typingRow, { paddingLeft: 72 }]}>
            <Text style={[Typography.small, { color: colors.mutedForeground }]}>
              Asterix is thinking...
            </Text>
          </View>
        )}

        <ChatInput onSend={handleSend} isLoading={isTyping} />
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  flex: { flex: 1 },
  list: { paddingTop: 12 },
  typingRow: {
    paddingHorizontal: 16,
    paddingBottom: 4,
  },
});
