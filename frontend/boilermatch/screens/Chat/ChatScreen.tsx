import React, { useEffect, useState } from 'react';
import { FlatList, TextInput, TouchableOpacity, Text, View } from 'react-native';
import { apiPost } from '@/api/api';
import AsyncStorage from "@react-native-async-storage/async-storage";

const ChatScreen = () => {
  const [chats, setChats] = useState<any[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [messageText, setMessageText] = useState('');
  const [email, setEmail] = useState('');
  const [token, setToken] = useState('');

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
    const history = await apiPost('/open_chat', { email, chat_id: chatId }, token);
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
      chat_id: selectedChatId
    }, token);

    if (res !== null) {
      setMessageText('');
      handleOpenChat(selectedChatId); // refresh messages
    }
  };

  const renderChatItem = ({ item }: any) => (
    <TouchableOpacity onPress={() => handleOpenChat(item.chat_id)}>
      <Text style={{ padding: 10 }}>{item.other_user_email}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={{ flex: 1 }}>
      {selectedChatId ? (
        <>
          <FlatList
            data={chatHistory}
            keyExtractor={(_, index) => index.toString()}
            renderItem={({ item }) => (
              <Text style={{ padding: 10 }}>{item.sender}: {item.content}</Text>
            )}
          />
          <TextInput
            placeholder="Type a message..."
            value={messageText}
            onChangeText={setMessageText}
            style={{ padding: 10, borderWidth: 1 }}
          />
          <TouchableOpacity onPress={handleSendMessage}>
            <Text style={{ padding: 10, backgroundColor: '#ccc' }}>Send</Text>
          </TouchableOpacity>
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

export default ChatScreen;

// const styles = StyleSheet.create({})