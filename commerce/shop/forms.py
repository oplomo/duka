from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Registration form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom CSS classes to the form fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# Login form
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom CSS classes to the form fields
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        widget=forms.RadioSelect  # Changed from Select to RadioSelect
    )
    comment = forms.CharField(widget=forms.Textarea)