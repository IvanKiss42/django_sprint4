from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model


User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta():
        model = Post
        fields = ('title', 'text', 'pub_date', 'location',
                  'category', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class UserForm(forms.ModelForm):

    class Meta():
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta():
        model = Comment
        fields = ('text',)