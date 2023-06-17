import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Room, Message

from crypto import crypto_rsa


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_slug"]
        self.room_group_name = "chat_%s" % self.room_name
        self.user = self.scope["user"]

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.add_user(self.room_name, self.user)

        await self.accept()

    async def disconnect(self, close_code):
        await self.remove_user(self.room_name, self.user)
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = self.user
        username = user.username
        room = self.room_name

        encrypted_message = crypto_rsa.encrypt(message, username)
        await self.save_message(room, user, encrypted_message)

        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "chat_message",
                "message": encrypted_message,
                #"room": room,
                "username": username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        #room = event["room"]
        username = event["username"]

        decrypted_message = crypto_rsa.decrypt(message, username)

        message_html = f"<div hx-swap-oob='beforeend:#messages'><p><b>{username}</b>: {decrypted_message}</p></div>"
        await self.send(
            text_data=json.dumps(
                {
                    "message": message_html,
                    #"room": room,
                    "username": username
                }
            )
        )

    @sync_to_async
    def save_message(self, room, user, message):
        room = Room.objects.get(slug=room)
        Message.objects.create(room=room, user=user, message=message)

    @sync_to_async
    def add_user(self, room, user):
        room = Room.objects.get(slug=room)
        if user not in room.users.all():
            room.users.add(user)
            room.save()

    @sync_to_async
    def remove_user(self, room, user):
        room = Room.objects.get(slug=room)
        if user in room.users.all():
            room.users.remove(user)
            room.save()
