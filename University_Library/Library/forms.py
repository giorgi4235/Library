from django import forms
from .models import Book
from django.utils import timezone
from datetime import timedelta

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Search')

class BookForm(forms.ModelForm):
    title = forms.CharField(max_length=100, required=True, label='Title')
    author = forms.CharField(max_length=100, required=True, label='Author')
    description = forms.CharField(widget=forms.Textarea, required=False, label='Description')
    image = forms.ImageField(required=False, label='Image')

    class Meta:
        model = Book
        fields = ('title', 'author', 'description', 'image')

    def __init__(self, *args, **kwargs):
        super(BookForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class BorrowBookForm(forms.Form):  # Change ModelForm to Form
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date() + timedelta(days=14)
    )

    def clean_return_date(self):
        return_date = self.cleaned_data['return_date']
        today = timezone.now().date()
        max_return_date = today + timedelta(days=30)

        if return_date <= today:
            raise forms.ValidationError("Return date must be in the future.")
        if return_date > max_return_date:
            raise forms.ValidationError("You can borrow a book for a maximum of 30 days.")

        return return_date


