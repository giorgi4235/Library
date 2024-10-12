from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField(default='No description available')
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    is_borrowed = models.BooleanField(default=False)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def borrow(self, student, return_date):
        if not self.is_borrowed:
            today = timezone.now().date()
            max_return_date = today + timedelta(days=30)

            if return_date > max_return_date:
                return False, "You can borrow a book for a maximum of 30 days."

            self.is_borrowed = True
            self.save()
            BorrowedBook.objects.create(book=self, student=student, return_date=return_date)
            return True, "Book borrowed successfully."
        return False, "This book is not available for borrowing."

    def return_book(self):
        if self.is_borrowed:
            self.is_borrowed = False
            self.save()
            BorrowedBook.objects.filter(book=self, return_date__gte=timezone.now()).delete()
            return True
        return False

class BorrowedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowed_books')
    borrow_date = models.DateField(default=timezone.now)
    return_date = models.DateField()

    def __str__(self):
        return f"{self.book} - {self.student} - {self.borrow_date} - {self.return_date}"

    @property
    def is_overdue(self):
        return timezone.now().date() > self.return_date