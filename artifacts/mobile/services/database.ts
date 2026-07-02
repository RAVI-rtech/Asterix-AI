/**
 * SQLite database service for AstraMind AI.
 * Persists conversations and messages locally on device (native only).
 * On web, all functions are no-ops — state is held in React context.
 */

import { Platform } from "react-native";

export interface DBConversation {
  id: string;
  title: string;
  category: string;
  created_at: string;
  updated_at: string;
}

export interface DBMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  category: string;
  suggested_actions: string; // JSON array string
}

// ── SQLite instance (native only) ─────────────────────────────────────────────

let _db: import("expo-sqlite").SQLiteDatabase | null = null;
let _initPromise: Promise<void> | null = null;

async function getDb(): Promise<import("expo-sqlite").SQLiteDatabase | null> {
  if (Platform.OS === "web") return null;

  if (_db) return _db;

  if (!_initPromise) {
    _initPromise = (async () => {
      const SQLite = await import("expo-sqlite");
      _db = await SQLite.openDatabaseAsync("astramind.db");
      await _db.execAsync(`
        PRAGMA journal_mode = WAL;

        CREATE TABLE IF NOT EXISTS conversations (
          id          TEXT PRIMARY KEY,
          title       TEXT NOT NULL DEFAULT 'New Conversation',
          category    TEXT NOT NULL DEFAULT 'chat',
          created_at  TEXT NOT NULL,
          updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
          id                TEXT PRIMARY KEY,
          conversation_id   TEXT NOT NULL,
          role              TEXT NOT NULL,
          content           TEXT NOT NULL,
          timestamp         TEXT NOT NULL,
          category          TEXT NOT NULL DEFAULT 'chat',
          suggested_actions TEXT NOT NULL DEFAULT '[]',
          FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
      `);
    })();
  }

  await _initPromise;
  return _db;
}

// ── Conversations ──────────────────────────────────────────────────────────────

export async function saveConversation(conv: DBConversation): Promise<void> {
  const db = await getDb();
  if (!db) return;
  await db.runAsync(
    `INSERT OR REPLACE INTO conversations (id, title, category, created_at, updated_at)
     VALUES (?, ?, ?, ?, ?)`,
    [conv.id, conv.title, conv.category, conv.created_at, conv.updated_at],
  );
}

export async function loadConversations(): Promise<DBConversation[]> {
  const db = await getDb();
  if (!db) return [];
  return db.getAllAsync<DBConversation>(
    `SELECT * FROM conversations ORDER BY updated_at DESC`,
  );
}

export async function deleteConversation(id: string): Promise<void> {
  const db = await getDb();
  if (!db) return;
  await db.runAsync(`DELETE FROM conversations WHERE id = ?`, [id]);
}

// ── Messages ───────────────────────────────────────────────────────────────────

export async function saveMessage(msg: DBMessage): Promise<void> {
  const db = await getDb();
  if (!db) return;
  await db.runAsync(
    `INSERT OR REPLACE INTO messages
       (id, conversation_id, role, content, timestamp, category, suggested_actions)
     VALUES (?, ?, ?, ?, ?, ?, ?)`,
    [
      msg.id,
      msg.conversation_id,
      msg.role,
      msg.content,
      msg.timestamp,
      msg.category,
      msg.suggested_actions,
    ],
  );
}

export async function loadMessages(conversationId: string): Promise<DBMessage[]> {
  const db = await getDb();
  if (!db) return [];
  return db.getAllAsync<DBMessage>(
    `SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC`,
    [conversationId],
  );
}

export async function deleteMessages(conversationId: string): Promise<void> {
  const db = await getDb();
  if (!db) return;
  await db.runAsync(
    `DELETE FROM messages WHERE conversation_id = ?`,
    [conversationId],
  );
}
