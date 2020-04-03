from rest_framework import serializers
from account.models import Account
from response_templates.templates import error_template, success_template


class AccountSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'username', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        account = Account(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError(error_template('passwords don\'t match'))

        account.set_password(password)
        account.save()
        return account

