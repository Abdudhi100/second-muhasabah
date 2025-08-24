import re
from rest_framework import serializers
from .models import User, NIGERIAN_STATES, ROLE_CHOICES, DefaultTodo, PersonalTodo
from rest_framework_simplejwt.tokens import RefreshToken


ROLE_KEYS = [c[0] for c in ROLE_CHOICES]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','username','role','location','whatsapp','date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=ROLE_KEYS)
    location = serializers.ChoiceField(choices=NIGERIAN_STATES)

    class Meta:
        model = User
        fields = ('email','username','password','role','location','whatsapp')

    def validate_whatsapp(self, value: str) -> str:
        if not re.fullmatch(r'^\+234\d{10}$', value):
            raise serializers.ValidationError('Must be +234 followed by 10 digits, e.g. +2348012345678.')
        return value

    def validate_role(self, value: str) -> str:
        # Accept alias if UI sends "sitting-regional-head"
        if value == 'sitting-regional-head':
            return 'regional-sitting-head'
        return value

    def create(self, validated_data):
        pwd = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    # identifier can be email or username
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        # try to find user by username, then by email
        user = None
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email__iexact=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError("No account found with those credentials.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect credentials.")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        return {
            "user": user,
            "access": access,
            "refresh": refresh_token,
        }
    


class DefaultTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultTodo
        fields = ["id", "name", "todo_type", "description", "extra_field_label"]

class PersonalTodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalTodo
        fields = ["id", "category", "title", "description", "completed", "created_at"]
        read_only_fields = ["id", "created_at"]