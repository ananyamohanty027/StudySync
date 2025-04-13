import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import StudyRoom, Participant, ChatMessage

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'video_call_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'offer':
            # Send offer to all peers
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'offer',
                    'offer': text_data_json['offer'],
                    'sender': self.scope['user'].username
                }
            )
        elif message_type == 'answer':
            # Send answer to the peer who sent the offer
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'answer',
                    'answer': text_data_json['answer'],
                    'sender': self.scope['user'].username
                }
            )
        elif message_type == 'ice_candidate':
            # Send ICE candidate to all peers
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'candidate': text_data_json['candidate'],
                    'sender': self.scope['user'].username
                }
            )
        elif message_type == 'video_state':
            # Send video state to all peers
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'video_state',
                    'enabled': text_data_json['enabled'],
                    'sender': self.scope['user'].username
                }
            )

    async def offer(self, event):
        # Send offer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer'],
            'sender': event['sender']
        }))

    async def answer(self, event):
        # Send answer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'sender': event['sender']
        }))

    async def ice_candidate(self, event):
        # Send ICE candidate to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'sender': event['sender']
        }))

    async def video_state(self, event):
        # Send video state to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'video_state',
            'enabled': event['enabled'],
            'sender': event['sender']
        }))

    async def session_ended(self, event):
        # Send session ended notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'session_ended',
            'message': event['message']
        }))

class ScreenShareConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'screen_share_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'screen_share':
            # Broadcast screen share data to all peers
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'screen_share',
                    'data': text_data_json['data'],
                    'sender': self.scope['user'].username
                }
            )

    async def screen_share(self, event):
        # Send screen share data to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'screen_share',
            'data': event['data'],
            'sender': event['sender']
        }))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        }))

    @database_sync_to_async
    def save_message(self, message):
        room = StudyRoom.objects.get(id=self.room_id)
        ChatMessage.objects.create(
            room=room,
            user=self.scope['user'],
            message=message
        )
