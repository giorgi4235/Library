from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .forms import SearchForm, BookForm, BorrowBookForm
from django.db.models import Prefetch
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import logging


logger = logging.getLogger(__name__)


def home_view(request):
    template_name = 'library/home.html'

    books = Book.objects.all()

    context = {
        'books': books
    }

    return render(request, template_name, context)


@login_required(login_url='login')
def available_books_view(request):
    template_name = 'library/available_book_list.html'

    books = Book.objects.filter(is_borrowed=False)

    context = {
        'books': books
    }

    return render(request, template_name, context)


@login_required(login_url='login')
def borrowed_books_view(request):
    template_name = 'library/Borrowed_book_list.html'

    books = Book.objects.filter(is_borrowed=True).prefetch_related(
        Prefetch('borrowedbook_set', queryset=BorrowedBook.objects.select_related('student'))
    )

    context = {
        'books': books
    }

    return render(request, template_name, context)

@login_required(login_url='login')
def details_view(request, pk):
    template_name = 'library/details.html'

    book = get_object_or_404(Book, pk=pk)
    referrer = request.META.get('HTTP_REFERER', '/')

    context = {
        'book': book,
        'referrer': referrer,
    }

    return render(request, template_name, context)


def book_search(request):
    template_name = 'library/book_search.html'
    form = SearchForm(request.GET or None)
    books = Book.objects.all()
    referrer = request.META.get('HTTP_REFERER', '/')

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            books = books.filter(title__icontains=query)

    context = {
        'form': form,
        'books': books,
        'referrer': referrer
    }

    return render(request, template_name, context)


@login_required
def book_create_view(request):
    # Check if the user is a vendor
    if not request.user.profile.is_vendor():
        messages.error(request, "Only vendors can upload books.")
        return redirect('home')

    template_name = 'library/book_create.html'
    form = BookForm()
    referrer = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.vendor = request.user
            book.save()
            messages.success(request, 'Book was successfully added')
            return redirect('details', pk=book.pk)

    context = {
        'form': form,
        'title': 'Create Book',
        'referrer': referrer
    }

    return render(request, template_name, context)


@login_required(login_url='login')
def book_edit_view(request, pk):
    template_name = 'library/book_edit.html'

    book = get_object_or_404(Book, pk=pk)
    referrer = request.META.get('HTTP_REFERER', '/')

    # Check if the user is a vendor and owns the book
    if not request.user.profile.is_vendor() or request.user != book.vendor:
        messages.error(request, "You don't have permission to edit this book.")
        return redirect('details', pk=book.pk)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" was successfully edited')
            return redirect('details', pk=book.pk)
        else:
            messages.error(request, f'Error editing book "{book.title}". Please check the form.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = BookForm(instance=book)

    context = {
        'form': form,
        'book': book,
        'referrer': referrer
    }

    return render(request, template_name, context)


@login_required
def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # Ensure that only the vendor who added the book can delete it
    if request.user != book.vendor:
        messages.error(request, "You do not have permission to delete this book.")
        return redirect('details', pk=pk)

    if request.method == 'POST':
        book.delete()
        messages.success(request, f'Book "{book.title}" was successfully deleted.')
        return redirect('vendor_profile')

    template_name = 'library/book_confirm_delete.html'
    context = {
        'book': book,
    }
    return render(request, template_name, context)


@login_required
def borrow_book(request, pk):
    template_name = 'library/borrow_book.html'
    book = get_object_or_404(Book, pk=pk)
    referrer = request.META.get('HTTP_REFERER', '/')

    try:
        if request.method == 'POST':
            form = BorrowBookForm(request.POST)
            if form.is_valid():
                return_date = form.cleaned_data['return_date']
                success, message = book.borrow(request.user, return_date)
                if success:
                    messages.success(request, message)
                    return redirect(referrer)
                else:
                    messages.error(request, message)
            else:
                messages.error(request, "Invalid form data")
        else:
            form = BorrowBookForm()
    except Exception as e:
        logger.error(f"Error borrowing book: {e}")
        messages.error(request, "An error occurred while borrowing the book")

    context = {
        'book': book,
        'form': form,
        'referrer': referrer
    }
    return render(request, template_name, context)

@login_required
def student_profile(request):
    template_name = 'library/student_profile.html'
    borrowed_books = request.user.borrowed_books.all()

    context = {
        'borrowed_books': borrowed_books
    }
    return render(request, template_name, context)



@login_required
def return_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if book.return_book():
        messages.success(request, "Book returned successfully.")
    else:
        messages.error(request, "The book is not currently borrowed.")

    return redirect('student_profile')


@login_required
def vendor_profile(request):
    template_name = 'library/vendor_profile.html'

    if not request.user.profile.is_vendor():
        return redirect('home')

    vendor_books = request.user.books.all()
    loaned_books = BorrowedBook.objects.filter(book__in=vendor_books) # გასესხებული წიგნები

    context = {
        "loaned_books": loaned_books,
    }

    return render(request, template_name, context)


