# drf-extended-viewsets
Django REST Framework extended viewsets utility which allows you to use `?extended=1` and `extend_fields=some,fields,specified` in your Django REST Framework ViewSets.


# Example
## Preparation
```python
# serializers.py

from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import Chat, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):
    messages = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = "__all__"


class ChatSerializerExtended(ChatSerializer):
    owner = CustomUserSerializer()  # This is just a serializer for a custom User model in the project
    messages = MessageSerializer(many=True, read_only=True)
```

```python
# views.py

from rest_framework.viewsets import ModelViewSet

from .utils.viewsets import ExtendedViewSetMixin
from .models import Chat
from .serializers import ChatSerializer, ChatSerializerExtended


class ChatAPIView(ExtendedViewSetMixin, ModelViewSet):
    serializer_class = ChatSerializer  # Default serializer class which will be used when `extended` query parameters is not passed or it is 0
    extended_serializer_class = ChatSerializerExtended  # Serializer which will be used when `extended` is 1
    queryset = Chat.objects.all()
```

## Default
Example URLs: http://127.0.0.1:8000/api/v1/chats/ or http://127.0.0.1:8000/api/v1/chats/?extended=0

This way, when you hit one of these endpoints, for example, `ChatSerializer` will be used and you'll get the following:
```json
[
    {
        "id": 1,
        "messages": [
            2,
            1
        ],
        "title": "Test chat",
        "created_at": "2022-06-30T12:46:08.568950Z",
        "updated_at": "2022-06-30T12:46:08.600204Z",
        "owner": 1
    }
]
```

## Extended
Example URL: http://127.0.0.1:8000/api/v1/chats/?extended=1

But when you set `extended` query parameter to 1, `ChatSerializerExtended` will be used which represents `messages` key using `MessageSerializer` and `owner` key using `CustomUserSerializer` class both of which inherit from `ModelSerializer` thus, all of the Django model properties will be displayed:
```json
[
    {
        "id": 1,
        "messages": [
            {
                "id": 2,
                "text": "Second message tho",
                "is_edited": false,
                "created_at": "2022-06-30T13:37:48.570028Z",
                "updated_at": "2022-06-30T13:37:48.570028Z",
                "user": 1,
                "chat": 1
            },
            {
                "id": 1,
                "text": "hii",
                "is_edited": true,
                "created_at": "2022-06-30T12:46:08.631455Z",
                "updated_at": "2022-06-30T12:46:08.651175Z",
                "user": 1,
                "chat": 1
            }
        ],
        "owner": {
            "id": 1,
            "last_login": "2022-06-30T11:22:14.473428Z",
            "is_superuser": true,
            "username": "admin",
            "first_name": "",
            "last_name": "",
            "is_staff": true,
            "is_active": true,
            "date_joined": "2022-06-30T11:08:39.971038Z",
            "email": "admin@tinychat.ru",
            "groups": [],
            "user_permissions": []
        },
        "title": "Test chat",
        "created_at": "2022-06-30T12:46:08.568950Z",
        "updated_at": "2022-06-30T12:46:08.600204Z"
    }
]
```

## Extend only certain fields
Example URL: http://localhost:8000/api/v1/chats/?extended=1&extend_fields=owner

You can pass the `extend_fields` parameter to specify which of the fields separated by comma to expand, leaving the processing of the rest on the default serializer.
```json
[
    {
        "id": 1,
        "messages": [
            2,
            1
        ],
        "owner": {
            "id": 1,
            "last_login": "2022-06-30T11:22:14.473428Z",
            "is_superuser": true,
            "username": "admin",
            "first_name": "",
            "last_name": "",
            "is_staff": true,
            "is_active": true,
            "date_joined": "2022-06-30T11:08:39.971038Z",
            "email": "admin@tinychat.ru",
            "groups": [],
            "user_permissions": []
        },
        "title": "Test chat",
        "created_at": "2022-06-30T12:46:08.568950Z",
        "updated_at": "2022-06-30T12:46:08.600204Z"
    }
]
```
