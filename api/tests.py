import json
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from .models import User, Conversation, Message, Games

class BackendTestCase(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = Client()
        # Seed some data for testing
        self.user1 = User.objects.create(
            username="alice",
            password_hash="pbkdf2_sha256$870000$mock_hash_alice"
        )
        self.user2 = User.objects.create(
            username="bob",
            password_hash="pbkdf2_sha256$870000$mock_hash_bob"
        )
        self.game = Games.objects.create(
            title="Chess",
            desc="Classic strategy board game.",
            url="http://example.com/chess"
        )

    def test_user_validation(self):
        # Empty username
        with self.assertRaises(ValidationError):
            u = User(username="", password_hash="hash")
            u.save()

        # Empty password_hash
        with self.assertRaises(ValidationError):
            u = User(username="charlie", password_hash="")
            u.save()

    def test_conversation_validation(self):
        # Conversation with self
        with self.assertRaises(ValidationError):
            c = Conversation(part_1=self.user1, part_2=self.user1)
            c.save()

        # Valid conversation
        c1 = Conversation.objects.create(part_1=self.user1, part_2=self.user2)
        self.assertIsNotNone(c1.id)

        # Duplicate conversation (exact same order)
        with self.assertRaises(ValidationError):
            c2 = Conversation(part_1=self.user1, part_2=self.user2)
            c2.save()

        # Duplicate conversation (reverse order)
        with self.assertRaises(ValidationError):
            c3 = Conversation(part_1=self.user2, part_2=self.user1)
            c3.save()

    def test_message_validation(self):
        c = Conversation.objects.create(part_1=self.user1, part_2=self.user2)
        
        # Sender is not a participant
        other_user = User.objects.create(username="charlie", password_hash="hash")
        with self.assertRaises(ValidationError):
            msg = Message(conv=c, sender=other_user, message_type='text', content='hello')
            msg.save()

        # Empty content
        with self.assertRaises(ValidationError):
            msg = Message(conv=c, sender=self.user1, message_type='text', content='')
            msg.save()

        # Valid message
        msg = Message.objects.create(conv=c, sender=self.user1, message_type='text', content='hello')
        self.assertIsNotNone(msg.id)

    def test_api_register(self):
        # Missing fields
        response = self.client.post(
            reverse('register'),
            data=json.dumps({"username": "newuser"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Success
        response = self.client.post(
            reverse('register'),
            data=json.dumps({"username": "newuser", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['username'], 'newuser')
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Duplicate username
        response = self.client.post(
            reverse('register'),
            data=json.dumps({"username": "newuser", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)

    def test_api_login(self):
        # Register a test user with a real hashed password using views.register
        self.client.post(
            reverse('register'),
            data=json.dumps({"username": "testuser", "password": "correct_pass"}),
            content_type="application/json"
        )

        # Incorrect password
        response = self.client.post(
            reverse('login'),
            data=json.dumps({"username": "testuser", "password": "wrong_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # Correct password
        response = self.client.post(
            reverse('login'),
            data=json.dumps({"username": "testuser", "password": "correct_pass"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['username'], 'testuser')
        self.assertEqual(self.client.session['user_id'], response.json()['id'])

    def test_api_search_users(self):
        # Unauthenticated
        response = self.client.get(reverse('search_users'))
        self.assertEqual(response.status_code, 401)

        # Authenticate user1
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        # Search for bob
        response = self.client.get(reverse('search_users') + "?search=bo")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], 'bob')

        # Exclude self
        response = self.client.get(reverse('search_users') + "?search=alice")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_api_conversations(self):
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        # Initiate new conversation with bob
        response = self.client.post(
            reverse('conversations'),
            data=json.dumps({"recipient_id": self.user2.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        conv_id = response.json()['id']

        # List conversations
        response = self.client.get(reverse('conversations'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], conv_id)
        self.assertEqual(data[0]['other_user']['username'], 'bob')

    def test_api_messages_and_pagination(self):
        conv = Conversation.objects.create(part_1=self.user1, part_2=self.user2)
        
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        # Send text message
        response = self.client.post(
            reverse('send_message'),
            data=json.dumps({
                "conv_id": conv.id,
                "message_type": "text",
                "content": "Hello bob"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        msg1_id = response.json()['id']

        # Send games message
        response = self.client.post(
            reverse('send_message'),
            data=json.dumps({
                "conv_id": conv.id,
                "message_type": "games",
                "content": "http://example.com/chess?invite=1"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        msg2_id = response.json()['id']

        # Record original last_update time of conversation
        conv.refresh_from_db()
        orig_update = conv.last_update

        # Fetch messages history (no cursor)
        response = self.client.get(reverse('conversation_messages', args=[conv.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], msg1_id)
        self.assertEqual(data[1]['id'], msg2_id)

        # Check that conversation was updated/refreshed
        conv.refresh_from_db()
        self.assertGreaterEqual(conv.last_update, orig_update)

        # Fetch messages history with cursor (after first message)
        response = self.client.get(reverse('conversation_messages', args=[conv.id]) + f"?after={msg1_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], msg2_id)

    def test_api_games(self):
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        response = self.client.get(reverse('games'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 4) # 3 seeded + 1 created in setUp
        titles = [g['title'] for g in data]
        self.assertIn('Chess', titles)
        self.assertIn('Tic-Tac-Toe', titles)
        self.assertIn('Connect Four', titles)

    def test_tc01_bcrypt_hashing(self):
        # Register a new user
        response = self.client.post(
            reverse('auth_register'),
            data=json.dumps({"username": "bcrypt_user", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        # Check database directly for bcrypt prefix
        user = User.objects.get(username="bcrypt_user")
        self.assertTrue(user.password_hash.startswith("bcrypt_sha256$"))

    def test_tc02_duplicate_username_409(self):
        # Register Alice first
        self.client.post(
            reverse('auth_register'),
            data=json.dumps({"username": "Alice", "password": "password123"}),
            content_type="application/json"
        )
        # Register duplicate with different casing
        response = self.client.post(
            reverse('auth_register'),
            data=json.dumps({"username": "alice", "password": "password123"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)

    def test_tc04_single_conversation(self):
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        # Try initiating new conversation with bob multiple times
        for _ in range(3):
            response = self.client.post(
                reverse('conversations'),
                data=json.dumps({"recipient_id": self.user2.id}),
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 201)

        # Count conversations between user1 and user2
        from django.db.models import Q
        count = Conversation.objects.filter(
            (Q(part_1=self.user1) & Q(part_2=self.user2)) |
            (Q(part_1=self.user2) & Q(part_2=self.user1))
        ).count()
        self.assertEqual(count, 1)

    def test_tc08_prevent_self_messaging(self):
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        # Start conversation with self
        response = self.client.post(
            reverse('conversations'),
            data=json.dumps({"recipient_id": self.user1.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_tc11_rate_limiting(self):
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        c = Conversation.objects.create(part_1=self.user1, part_2=self.user2)

        # Clear cache first
        from django.core.cache import cache
        cache.clear()

        # Send 50 messages - all should succeed
        for i in range(50):
            response = self.client.post(
                reverse('send_message'),
                data=json.dumps({
                    "conv_id": c.id,
                    "message_type": "text",
                    "content": f"msg {i}"
                }),
                content_type="application/json"
            )
            self.assertEqual(response.status_code, 201)

        # 51st message within 2 seconds should be rate limited
        response = self.client.post(
            reverse('send_message'),
            data=json.dumps({
                "conv_id": c.id,
                "message_type": "text",
                "content": "rate limit msg"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 429)

    def test_tc12_duplicate_message_prevention(self):
        session = self.client.session
        session['user_id'] = self.user1.id
        session.save()

        c = Conversation.objects.create(part_1=self.user1, part_2=self.user2)
        tx_id = "test-tx-123"

        # Send first message with client_tx_id
        response1 = self.client.post(
            reverse('send_message'),
            data=json.dumps({
                "conv_id": c.id,
                "message_type": "text",
                "content": "Original message",
                "client_tx_id": tx_id
            }),
            content_type="application/json"
        )
        self.assertEqual(response1.status_code, 201)
        msg1_id = response1.json()['id']

        # Send second message with duplicate client_tx_id
        response2 = self.client.post(
            reverse('send_message'),
            data=json.dumps({
                "conv_id": c.id,
                "message_type": "text",
                "content": "Duplicate attempt",
                "client_tx_id": tx_id
            }),
            content_type="application/json"
        )
        self.assertEqual(response2.status_code, 201)
        msg2_id = response2.json()['id']

        # Verify only one message is saved in database and both returned same message ID
        self.assertEqual(msg1_id, msg2_id)
        self.assertEqual(Message.objects.filter(conv=c, client_tx_id=tx_id).count(), 1)

    def test_tc18_access_control(self):
        # Create a conversation between user1 and user2
        c = Conversation.objects.create(part_1=self.user1, part_2=self.user2)

        # Create user3 who is not in the conversation
        user3 = User.objects.create(username="charlie", password_hash="pbkdf2_sha256$870000$mock_hash_charlie")

        # Authenticate as user3
        session = self.client.session
        session['user_id'] = user3.id
        session.save()

        # Try to access messages for conversation
        response = self.client.get(reverse('conversation_messages', args=[c.id]))
        self.assertEqual(response.status_code, 403)

