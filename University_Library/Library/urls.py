from django.urls import path
from .views import (home_view, borrowed_books_view, available_books_view, details_view,
                    book_search, book_create_view, book_edit_view, borrow_book, student_profile,
                    vendor_profile, return_book, book_delete_view)

urlpatterns = [
    path('home/', home_view, name='home'),
    path('borrowed/', borrowed_books_view, name='borrowed'),
    path('available/', available_books_view, name='available'),
    path('details/<int:pk>', details_view, name='details'),
    path('search/', book_search, name='book_search'),
    path('create/', book_create_view, name='create'),
    path('edit/<int:pk>', book_edit_view, name='edit'),
    path('delete/<int:pk>/', book_delete_view, name='delete'),
    path('book/<int:pk>/borrow/', borrow_book, name='borrow_book'),
    path('profile/student/', student_profile, name='student_profile'),
    path('profile/vendor/', vendor_profile, name='vendor_profile'),
    path('return/<int:pk>/', return_book, name='return_book'),
]

