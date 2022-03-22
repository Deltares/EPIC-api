from rest_framework import serializers

from epic_app.models import EpicUser, Question, Answer

class EpicUserSerializer(serializers.ModelSerializer):
    """
    Serializer for 'EpicUser'
    """
    class Meta:
        """
        Overriden meta class for serializing purposes.
        """
        model=EpicUser
        fields = ('url', 'id', 'username', 'organization')

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for 'Question'
    """
    class Meta:
        """
        Overriden meta class for serializing purposes.
        """
        model=Question
        fields=('url', 'id', 'description', )
    
class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for 'QuestionAnswerForm'
    """
    class Meta:
        """
        Overriden meta class for serializing purposes.
        """
        model=Answer
        fields=('url', 'id', 'user', 'question', 'short_answer', 'long_answer')