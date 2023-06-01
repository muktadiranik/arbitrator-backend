from rest_framework import serializers

from .models import User
from dj_rest_auth.serializers import PasswordResetSerializer as _PasswordResetSerializer
from .forms import CustomAllAuthPasswordResetForm


class UsersSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'last_login', 'username', 'is_superuser', 'first_name', 'first_name', 'is_staff', 'is_active',
                  'date_joined', 'email', 'password', 'permissions']
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }


class PasswordResetSerializer(_PasswordResetSerializer):

    def get_email_options(self):
        return {
            'email_template_name': 'account/password_reset_key_message.txt',
        }

    def validate_email(self, value):
        self.reset_form = CustomAllAuthPasswordResetForm(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def get_permissions(self, obj):
        return obj.get_all_permissions()
