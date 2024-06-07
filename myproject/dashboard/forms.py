from django import forms
from .models import Book, Library,User,Transaction,Visit,AdminUser
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from django.contrib.auth import get_user_model,authenticate
from .backends import make_password


class BookForm(forms.ModelForm):
    author_name = forms.CharField(max_length=100, required=False, label="Author's Name")

    class Meta:
        model = Book
        fields = ['central_id', 'local_id', 'title', 'quantity_available', 'notes', 'categories']
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'user_cin': forms.HiddenInput(),
            'library': forms.HiddenInput(),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'birth_date', 'cin', 'address', 'phone', 'membership_id', 'membership_validity']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'user_cin': forms.HiddenInput(),
            'library': forms.HiddenInput(),

        }

class TransactionForm(forms.ModelForm):
    membership_id = forms.CharField(max_length=10, required=True, label="Membership ID")
    book_id = forms.CharField(max_length=10, required=True, label="Book ID")

    GET = 'get'
    RETURN = 'return'
    GET_RETURN_CHOICES = [
        (GET, 'Get'),
        (RETURN, 'Return'),
    ]
    
    get_or_return = forms.ChoiceField(
        label='Get or Return',
        choices=GET_RETURN_CHOICES,
        widget=forms.RadioSelect,
        initial=GET,
    )
    class Meta:
        model = Transaction
        fields = ['return_date']
        widgets = {
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'user_cin': forms.HiddenInput(),
            'library': forms.HiddenInput(),

        }

class VisitForm(forms.Form):
    user_id = forms.CharField(label='User ID', max_length=20)
    book_id = forms.CharField(label='Book ID', max_length=20, required=False)
    widgets = {
        'user_cin': forms.HiddenInput(),
        'library': forms.HiddenInput(),

    }


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = AdminUser
        fields = ('email', 'first_name', 'last_name', 'birth_date', 'cin', 'phone', 'library')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = ['name','address' , 'city', 'zipCode']

from django import forms

class LoginForm(forms.Form):
    cin = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        cin = cleaned_data.get("cin")
        password = cleaned_data.get("password")
        return cleaned_data

