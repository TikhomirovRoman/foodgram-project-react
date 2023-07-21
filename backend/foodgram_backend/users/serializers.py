
from django.db import IntegrityError, transaction
from rest_framework import serializers
from .models import User

# class CreateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name')

#     def create(self, validated_data):
#         try:
#             user = self.perform_create(validated_data)
#         except IntegrityError:
#             self.fail("cannot_create_user")
#         return user

#     def perform_create(self, validated_data):
#         with transaction.atomic():
#             user = User.objects.create_user(**validated_data)
#             user.set_unusable_password()
#             user.save()
#         return user