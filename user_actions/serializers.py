from rest_framework import serializers


TARGET_TYPE_CHOICES = {
    'comment': 'comment',
    'post': 'post'
}

CHOICES = list(TARGET_TYPE_CHOICES.values())


class LikeUpdateSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(CHOICES)
    action = serializers.ChoiceField([-1, 0, 1])
    target_id = serializers.IntegerField()


class SaveUpdateSerializer(serializers.Serializer):
    target_type = serializers.ChoiceField(CHOICES)
    action = serializers.ChoiceField([0, 1])
    target_id = serializers.IntegerField()


