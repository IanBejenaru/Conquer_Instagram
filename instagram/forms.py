from django import forms
from django.contrib.auth.models import User


#import
class RegistrationForm(forms.ModelForm):
    #Ponemos formato contraseña:
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        #Campos que voy a utilizar para registrar un usuario:
        fields = [
            "first_name",
            "username",
            "email",
            "password"
        ]
    
    def save(self):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data["password"])
        user.save()

        #Cuando creemos un usuario asignamos un perfil a ese usuario:
        from profiles.models import UserProfile
        UserProfile.objects.create(user = user)

        return user


class LoginForm(forms.Form):
    username = forms.CharField(label=("email"))
    password = forms.CharField(label=("password"), widget=forms.PasswordInput())


class FollowForm(forms.Form):
    profile_pk = forms.IntegerField(widget=forms.HiddenInput())