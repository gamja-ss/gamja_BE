from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers
from users.models import User

from .models import Challenge


#  챌린지 Serializer
class ChallengeSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    winner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Challenge
        fields = "__all__"


#  챌린지 생성 Serializer
class ChallengeCreateSerializer(serializers.ModelSerializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        help_text="참가자 ID 리스트",
    )  # 참가자 ID 리스트를 추가

    class Meta:
        model = Challenge
        fields = ["condition", "start_date", "duration", "total_bet_coins", "user_ids"]

    def create(self, validated_data):
        request_user = self.context["request"].user

        user_ids = self.initial_data.get("user_ids", [])

        challenge = Challenge.objects.create(**validated_data)
        challenge.participants.add(request_user)  # 생성자를 기본 참가자로 등록

        # 참가자 추가
        users = User.objects.filter(id__in=user_ids)
        challenge.participants.add(*users)

        # 참가 요청을 WebSocket을 통해 발송
        channel_layer = get_channel_layer()
        for user in users:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "challenge_request",
                    "message": {"text": f"{request_user.username}님이 챌린지 초대를 보냈습니다."},
                },
            )

        return challenge


#  챌린지 요청 Serializer
class ChallengeRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    challenge_id = serializers.IntegerField()


#  챌린지 응답 Serializer
class ChallengeResponseSerializer(serializers.Serializer):
    accepted = serializers.BooleanField()  # T/F


# 챌린지 로그 Serializer
class ChallengeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            "id",
            "status",
            "total_bet_coins",
            "reward_coins",
            "created_at",
            "updated_at",
        ]


# 챌린지 결과 Serializer (챌린지 종료 후)
class ChallengeResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ["id", "status", "reward_coins"]
