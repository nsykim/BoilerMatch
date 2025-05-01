import React, { useEffect, useState } from 'react';
import {
  FlatList,
  TextInput,
  TouchableOpacity,
  Text,
  View,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useAuth } from '@/contexts/AuthContext';
import { apiPost } from '@/api/api';
import { darkTheme } from '@/styles/theme'; // adjust if needed

const ChatScreen = () => {
  const [chats, setChats] = useState<any[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [messageText, setMessageText] = useState('');
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');
  const { token: st } = useAuth();

  useEffect(() => {
    const loadChats = async () => {
      const storedEmail = await AsyncStorage.getItem('email');
      const storedToken = await AsyncStorage.getItem('session_token');
      if (!storedEmail || !storedToken) return;

      setEmail(storedEmail);
      setToken(storedToken);

      const chatsResponse = await apiPost('/chats_page', { email: storedEmail }, storedToken);
      if (chatsResponse) setChats(chatsResponse);
    };
    loadChats();
  }, []);

  const handleOpenChat = async (chatId: string) => {
    const history = await apiPost('/open_chat', { email }, token, chatId);
    if (history) {
      setSelectedChatId(chatId);
      setChatHistory(history);
    }
  };

  const handleSendMessage = async () => {
    if (!messageText || !selectedChatId) return;

    const res = await apiPost('/send_message', {
      email,
      content: messageText,
    }, token, selectedChatId);

    if (res !== null) {
      setMessageText('');
      handleOpenChat(selectedChatId);
    }
  };

  const renderChatItem = ({ item }: any) => (
    <TouchableOpacity onPress={() => handleOpenChat(item.chat_id)} style={styles.chatItem}>
      <Text style={styles.text}>{item.participant?.name || item.participant?.email}</Text>
    </TouchableOpacity>
  );

  const selectedChat = chats.find(c => c.chat_id === selectedChatId);
  const participantName = selectedChat?.participant?.name || "Chat";

  return (
    <View style={styles.container}>
      {selectedChatId ? (
        <>
          <View style={styles.chatHeader}>
            <TouchableOpacity onPress={() => setSelectedChatId(null)}>
              <Text style={styles.backText}>← Back</Text>
            </TouchableOpacity>
            <Text style={styles.chatTitle}>{participantName}</Text>
          </View>
          <FlatList
            data={chatHistory}
            keyExtractor={(_, index) => index.toString()}
            renderItem={({ item }) => (
              <Text style={styles.messageText}>{item.sender}: {item.content}</Text>
            )}
            contentContainerStyle={styles.chatList}
          />
          <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={90}
          >
            <View style={styles.inputContainer}>
              <TextInput
                placeholder="Type a message..."
                placeholderTextColor={darkTheme.text}
                value={messageText}
                onChangeText={setMessageText}
                style={styles.input}
              />
              <TouchableOpacity onPress={handleSendMessage} style={styles.sendButton}>
                <Text style={styles.sendText}>Send</Text>
              </TouchableOpacity>
            </View>
          </KeyboardAvoidingView>
        </>
      ) : (
        <FlatList
          data={chats}
          keyExtractor={item => item.chat_id}
          renderItem={renderChatItem}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: darkTheme.background,
    padding: 10,
  },
  chatItem: {
    padding: 12,
    borderBottomColor: '#444',
    borderBottomWidth: 1,
  },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    marginBottom: 4,
  },
  backText: {
    color: darkTheme.primary,
    fontSize: 18,
    marginRight: 10,
  },
  chatTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: darkTheme.text,
  },
  chatList: {
    flexGrow: 1,
    paddingBottom: 10,
  },
  messageText: {
    paddingVertical: 8,
    color: darkTheme.text,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#444',
    padding: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#333',
    color: darkTheme.text,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
  },
  sendButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginLeft: 8,
    backgroundColor: darkTheme.primary,
    borderRadius: 20,
  },
  sendText: {
    color: '#fff',
    fontWeight: 'bold',
  },
  text: {
    color: darkTheme.text,
  },
});

export default ChatScreen;
