import unittest
from unittest.mock import patch, MagicMock
import json
import time
import logging
import os
from importlib import reload

class TestFirebaseMessaging(unittest.TestCase):
    def setUp(self):
        # Start all patches first
        self.env_patcher = patch.dict('os.environ', {
            'FIREBASE_CREDENTIALS': json.dumps({
                "type": "service_account",
                "project_id": "test-project"
            })
        })
        
        self.certificate_patcher = patch('firebase_admin.credentials.Certificate')
        self.initialize_patcher = patch('firebase_admin.initialize_app')
        self.firestore_patcher = patch('firebase_admin.firestore.client')
        self.update_chat_patcher = patch('src.database.db_operations.update_chat')
        
        # Start all patches
        self.env_patcher.start()
        self.mock_certificate = self.certificate_patcher.start()
        self.mock_initialize = self.initialize_patcher.start()
        self.mock_firestore_client = self.firestore_patcher.start()
        self.mock_update_chat = self.update_chat_patcher.start()
        
        # Set up mock firestore client
        self.mock_db = MagicMock()
        self.mock_firestore_client.return_value = self.mock_db
        
        # Mock collection references
        self.mock_collection = MagicMock()
        self.mock_document = MagicMock()
        self.mock_messages_collection = MagicMock()
        self.mock_message_doc = MagicMock()
        
        # Set up the chain of mock returns
        self.mock_db.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_document
        self.mock_document.collection.return_value = self.mock_messages_collection
        self.mock_messages_collection.document.return_value = self.mock_message_doc
        
        # Now import the module after all mocks are in place
        import src.utils.firebase as firebase_messaging
        self.firebase_messaging = reload(firebase_messaging)
    
    def tearDown(self):
        # Stop all patches
        self.env_patcher.stop()
        self.certificate_patcher.stop()
        self.initialize_patcher.stop()
        self.firestore_patcher.stop()
        self.update_chat_patcher.stop()
    
    def test_send_message_success(self):
        # Setup
        chat_id = "test_chat_123"
        sender = "test_user"
        content = "Hello, world!"
        collection = "test_collection"
        self.mock_update_chat.return_value = True
        
        # Execute
        result = self.firebase_messaging.send_message(chat_id, sender, content, collection)
        
        # Assert
        self.mock_db.collection.assert_called_with("chats")
        self.mock_collection.document.assert_called_with(chat_id)
        self.mock_document.collection.assert_called_with("messages")
        self.mock_message_doc.set.assert_called_once()
        
        # Verify the message data
        call_args = self.mock_message_doc.set.call_args[0][0]
        self.assertEqual(call_args["sender"], sender)
        self.assertEqual(call_args["content"], content)
        self.assertIsInstance(call_args["timestamp"], int)
        
        # Verify mongo update was called
        self.mock_update_chat.assert_called_once()
        args = self.mock_update_chat.call_args[0]
        self.assertEqual(args[0], chat_id)
        self.assertEqual(args[1], collection)
        self.assertIsInstance(args[2], int)
        
        # Function returns True on success
        self.assertTrue(result)
    
    def test_send_message_firebase_failure(self):
        # Setup
        chat_id = "test_chat_123"
        sender = "test_user"
        content = "Hello, world!"
        collection = "test_collection"
        
        # Make Firebase operation fail
        self.mock_message_doc.set.side_effect = Exception("Firebase error")
        
        # Execute
        result = self.firebase_messaging.send_message(chat_id, sender, content, collection)
        
        # Assert
        self.assertFalse(result)
        self.mock_update_chat.assert_not_called()
    
    def test_send_message_mongo_failure(self):
        # Setup
        chat_id = "test_chat_123"
        sender = "test_user"
        content = "Hello, world!"
        collection = "test_collection"
        self.mock_update_chat.return_value = False
        
        # Execute
        result = self.firebase_messaging.send_message(chat_id, sender, content, collection)
        
        # Assert
        self.assertFalse(result)
        self.mock_update_chat.assert_called_once()
    
    def test_fetch_chat_history_success(self):
        # Setup
        chat_id = "test_chat_123"
        mock_messages = [
            MagicMock(id='msg1', to_dict=lambda: {"sender": "user1", "content": "Hello", "timestamp": 1234567890}),
            MagicMock(id='msg2', to_dict=lambda: {"sender": "user2", "content": "Hi", "timestamp": 1234567891})
        ]
        self.mock_messages_collection.order_by.return_value.stream.return_value = mock_messages
        
        # Execute
        result = self.firebase_messaging.fetch_chat_history(chat_id)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "msg1")
        self.assertEqual(result[1]["id"], "msg2")
        self.mock_messages_collection.order_by.assert_called_with("timestamp")
    
    def test_fetch_chat_history_failure(self):
        # Setup
        chat_id = "test_chat_123"
        self.mock_messages_collection.order_by.side_effect = Exception("Firebase error")
        
        # Execute
        result = self.firebase_messaging.fetch_chat_history(chat_id)
        
        # Assert
        self.assertIsNone(result)
    
    def test_send_message_mongo_exception(self):
        """Test handling of MongoDB update_chat throwing an exception"""
        chat_id = "test_chat_123"
        sender = "test_user"
        content = "Hello, world!"
        collection = "test_collection"
        self.mock_update_chat.side_effect = Exception("MongoDB connection error")
        
        result = self.firebase_messaging.send_message(chat_id, sender, content, collection)
        
        self.assertFalse(result)
        self.mock_update_chat.assert_called_once()
        
    def test_send_message_timestamp_validation(self):
        """Test that timestamps are recent and valid"""
        chat_id = "test_chat_123"
        sender = "test_user"
        content = "Hello, world!"
        collection = "test_collection"
        self.mock_update_chat.return_value = True
        
        current_time = int(time.time())
        result = self.firebase_messaging.send_message(chat_id, sender, content, collection)
        
        self.assertTrue(result)
        call_args = self.mock_message_doc.set.call_args[0][0]
        timestamp = call_args["timestamp"]
        
        # Timestamp should be within 5 seconds of current time
        self.assertLessEqual(abs(timestamp - current_time), 5)
        
    def test_fetch_chat_history_empty(self):
        """Test fetching chat history when no messages exist"""
        chat_id = "test_chat_123"
        self.mock_messages_collection.order_by.return_value.stream.return_value = []
        
        result = self.firebase_messaging.fetch_chat_history(chat_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)
        
    def test_fetch_chat_history_malformed_data(self):
        """Test handling of malformed message data in Firebase"""
        chat_id = "test_chat_123"
        mock_messages = [
            MagicMock(id='msg1', to_dict=lambda: {"sender": "user1"}),  # Missing content and timestamp
            MagicMock(id='msg2', to_dict=lambda: {"content": "Hi"}),    # Missing sender and timestamp
            MagicMock(id='msg3', to_dict=lambda: {})                    # Empty message
        ]
        self.mock_messages_collection.order_by.return_value.stream.return_value = mock_messages
        
        result = self.firebase_messaging.fetch_chat_history(chat_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertTrue(all('id' in msg for msg in result))
        
    def test_fetch_chat_history_order(self):
        """Test that messages are properly ordered by timestamp"""
        chat_id = "test_chat_123"
        mock_messages = [
            MagicMock(id='msg1', to_dict=lambda: {"sender": "user1", "content": "First", "timestamp": 1000}),
            MagicMock(id='msg2', to_dict=lambda: {"sender": "user2", "content": "Second", "timestamp": 2000}),
            MagicMock(id='msg3', to_dict=lambda: {"sender": "user3", "content": "Third", "timestamp": 3000})
        ]
        self.mock_messages_collection.order_by.return_value.stream.return_value = mock_messages
        
        result = self.firebase_messaging.fetch_chat_history(chat_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        # Verify timestamps are in ascending order
        timestamps = [msg["timestamp"] for msg in result]
        self.assertEqual(timestamps, sorted(timestamps))

if __name__ == '__main__':
    unittest.main()