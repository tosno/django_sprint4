from django import forms

from blog.models import Post, Comment, User


class BlogForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published', 'created_at',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )
        widgets = {'text': forms.Textarea(attrs={'rows': 3})}


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )
