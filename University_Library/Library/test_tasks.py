from django.test import TestCase
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from .models import BorrowedBook, Book, User
from .tasks import send_due_date_notifications
from django.urls import reverse

class NotificationTaskTest(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(username='testuser', email='testuser@example.com', password='12345')

        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            description='Test Description',
            vendor=self.student,
            is_borrowed=False
        )

        self.borrowed_book = BorrowedBook.objects.create(
            book=self.book,
            student=self.student,
            borrow_date=timezone.now().date(),
            return_date=timezone.now().date() + timedelta(days=2)
        )

    def test_send_due_date_notifications(self):
        send_due_date_notifications()

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reminder: Book Return Due Soon', mail.outbox[0].subject)

    def test_no_notifications_for_books_far_from_due(self):
        self.borrowed_book.return_date = timezone.now().date() + timedelta(days=10)
        self.borrowed_book.save()

        send_due_date_notifications()

        self.assertEqual(len(mail.outbox), 0)


class HomeViewTest(TestCase):

    def setUp(self):
        # Create a user to be the vendor
        self.vendor = User.objects.create_user(username='vendor', password='testpass')

        # Create a book with a vendor
        Book.objects.create(
            title='Test Book',
            author='Test Author',
            vendor=self.vendor,  # Set the vendor field
            is_borrowed=False
        )

    def test_home_view_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_books_display(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Test Book')


class BorrowBookViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.book = Book.objects.create(title='Test Book', author='Test Author', is_borrowed=False)
        self.borrow_url = reverse('borrow_book', args=[self.book.pk])

    def test_borrow_book_view_redirects_if_not_logged_in(self):
        response = self.client.get(self.borrow_url)
        self.assertRedirects(response, '/login/?next=' + self.borrow_url)

    def test_borrow_book_view_logged_in(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.borrow_url)
        self.assertEqual(response.status_code, 200)

    def test_borrow_book_success(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.borrow_url, {
            'return_date': timezone.now().date() + timedelta(days=30)
        })
        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_borrowed)


class BookCreateViewTest(TestCase):

    def setUp(self):
        # Create a vendor user
        self.vendor = User.objects.create_user(username='vendor', password='testpass')

        # Log in the vendor
        self.client.login(username='vendor', password='testpass')

        self.create_url = reverse('book_create')

    def test_create_book_as_vendor(self):
        response = self.client.post(self.create_url, {
            'title': 'New Book',
            'author': 'New Author',
            'description': 'A great book',
            'is_borrowed': False
        })
        self.assertEqual(response.status_code, 302)  # Should redirect to the details view
        self.assertTrue(Book.objects.filter(title='New Book').exists())  # Check the book was created


class LoginPageTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'testpass'
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        })
        self.assertContains(response, 'Invalid Email', status_code=200)
