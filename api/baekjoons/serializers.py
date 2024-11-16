from rest_framework import serializers

from .models import Baekjoon


class BaekjoonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baekjoon
        fields = ["solved", "score", "tier", "date"]
