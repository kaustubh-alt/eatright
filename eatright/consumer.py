import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.storage import FileSystemStorage
import base64
import time
from io import BytesIO
from django.conf import settings
from . import modelinteract as mi
import concurrent.futures
from .models import userchat, userdb
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import uuid

image_storage_path = settings.MEDIA_URL + 'uploads/'
fs = FileSystemStorage(location=image_storage_path)


# Async-safe class
class Modulus:
    def __init__(self, user_instance):
        self.user = user_instance
        self.last_chats = None

    @classmethod
    async def create(cls, username):
        # print(username)
        user_instance = await sync_to_async(userdb.objects.get)(user=username)
        return cls(user_instance)
    


    async def save_user_chat(self, timestamp, message=None, response=None, genimage=None, userimage=None):
        await sync_to_async(userchat.objects.create)(
            userid=self.user,
            user=message,
            response=response,
            userimage=userimage,
            genimage=genimage,
            time=timestamp,
        )

    

    async def get_last_messages(self):
        """Fetch last 10 messages for the current user"""
        messages = await sync_to_async(list)(
            userchat.objects.filter(userid=self.user)
            .order_by('-time')
            .values('user', 'response', 'userimage', 'genimage', 'time')
        )
        # Convert datetime to timestamp for JSON serialization
        return [{
            'user_message': msg['user'],
            'bot_response': msg['response'],
            'user_image': f"{image_storage_path}{msg['userimage']}" if msg['userimage'] else None,
            'generated_image': msg['genimage'],
            'timestamp': msg['time'].timestamp() if msg['time'] else None
        } for msg in messages]
            

def process_llama_request(input_data,chats):
    llama = mi.lamba()
    response = llama.gemini(input_data,chats)
    return response


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Fetch user object asynchronously and attach to scope
        self.userobj = await Modulus.create(self.scope['user'])
        await self.accept()

        self.userobj.last_chats = await self.userobj.get_last_messages()

        #print(self.userobj.last_chats)
        # Send welcome message and chat history
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Welcome to the chat!",
            "chat_history": self.userobj.last_chats
        }))

        chat_context = ""
       # print(chat_history[0:10])
        if self.userobj.last_chats:
            for msg in list(reversed(self.userobj.last_chats[0:10])):
                chat_context += f"User: {msg.get('user_message', '')}\n"
                chat_context += f"Assistant: {msg.get('bot_response', '')}\n"

        # Clean the chat context string
        chat_context = chat_context.replace('\n', '\\n').replace('\r', '').replace('None', 'null')

        self.userobj.last_chats = chat_context

    async def receive(self, text_data):
        packet = json.loads(text_data)

        if not packet['isImage']:
            word_count = len(packet['message'].split())
            if word_count > 50:
                await self.send(text_data=json.dumps({
                    "message": "Please limit your message to 50 words or less.",
                    "IsImage": False,
                    "isError": True
                }))
                return

        IsImage = False
        message = ""

        if packet['isImage']:
            try:
                base64_image = packet['message']
                image_data = base64.b64decode(base64_image.split(',')[1])

                filename = f"image_{int(time.time())}_{uuid.uuid4().hex[:8]}.png"
                file_path = fs.save(filename, BytesIO(image_data))
                # print(file_path)

                message = f"Image uploaded: {file_path}"
                #IsImage = True

                await self.userobj.save_user_chat(
                    timestamp=time.time(),
                    userimage=file_path
                )



            except Exception as e:
                message = f"Error uploading image: {str(e)}"

        else:
          
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(process_llama_request, packet['message'], self.userobj.last_chats)
                message = future.result()
                #print("msg is ",message)

            await self.userobj.save_user_chat(
                timestamp=time.time(),
                message=packet['message'],
                response=message['response']
            )
  

            await self.send(text_data=json.dumps({
                "message": message['response'],
                "IsImage": IsImage,
            }))

            if message['recommendation']:
                await self.userobj.save_user_chat(
                    timestamp=time.time(),
                    genimage=message['recommendation']
                )

                await self.send(text_data=json.dumps({
                    "message": message['recommendation'],
                    "IsImage": True,
            }))

            

            secn = self.userobj.last_chats[5:].find('User:')
            self.userobj.last_chats = self.userobj.last_chats.replace(self.userobj.last_chats[0:5+secn], '')
            self.userobj.last_chats += f"User: {packet['message']}\nAssistant: {message['response']}\n"

    async def disconnect(self, close_code):
        pass
