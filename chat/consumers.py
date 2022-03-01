from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import Message

User = get_user_model()

class ChatConsumer(WebsocketConsumer):

    # To fetch the last messages on the server
    def fetch_messages(self, data):
        # "messages" gets the last 10 messages fetched from the database server
        messages = Message.last_10_messages()

        # We wanna send back all the messages in to the websocket
        content = {
            'command': 'messages',
            # We can serialize "messages" so it gets created in the form of a JSON Object
            'messages': self.messages_to_json(messages)  
        }
        # Sending the list to the "send_message()" which will 
        # handle the functionalities of sending the content/fetching the last 10 messages
        self.send_message(content)



    def new_message(self, data):
        # Grabs the username with the "from" keyword
        author = data['from']
        # Filter the user objects by the username
        author_user = User.objects.filter(username=author)[0]
        # Creating a new message object to hold the message and its details
        message = Message.objects.create(
            author = author_user, 
            content = data['message'])
        content = {
            # refers to the "new_message()"
            'command': 'new_message',
            # the message sent by one user will go to 
            # "message_to_json()" to get it converted into a JSON object and 
            # then the message will display the content from there, as well 
            # as store the message information 
            'message': self.message_to_json(message)
        }
        # Sends the content of the message sent by the user, as "content"
        # to the chat room.
        return self.send_chat_message(content)


    # Takes in the "messages" arg from "fetch_messages" to serialize 
    # the last 10 messages and put them in the websocket and display 
    # them in order of recent timestamps
    def messages_to_json(self, messages):
        result = []     # We create an empty list
        for message in messages:        # for each message in "messages"
            # We append all the lat 10 "messages" one-by-one through the convenience method 
            # i.e. "message_to_json()" to handle each and every message and serialize them 
            # in a particular manner and format
            result.append(self.message_to_json(message))
        return result          # return the result list with all the "messages" serialized


    # Takes in the instance of message from "messages" 
    # and converts each message into an object
    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        } 

    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)
        

    # the "content" is received as a parameter, as "message"
    def send_chat_message(self, message):    
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                # Sends the message via "chat_message()"
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))


    # Creates an event and grabs the message and creates 
    # a JSON dump of the message
    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))