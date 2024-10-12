from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import BorrowedBook
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def send_due_date_notifications():
    try:
        today = timezone.now().date()
        notification_threshold = today + timedelta(days=3)  # Notify 3 days before due date

        # Find borrowed books with return dates close to today
        upcoming_due_books = BorrowedBook.objects.filter(
            return_date__range=(today, notification_threshold)
        )

        for borrowed_book in upcoming_due_books:
            student = borrowed_book.student
            book = borrowed_book.book

            # Prepare the email content
            subject = f'Reminder: Book Return Due Soon'
            message = (
                f'Dear {student.username},\n\n'
                f'This is a reminder that the book "{book.title}" you borrowed is due for return on {borrowed_book.return_date}.\n'
                f'Please return it on time to avoid any late fees.\n\n'
                f'Thank you,\nLibrary Team'
            )
            from_email = 'your-email@example.com'

            # Send the email
            send_mail(subject, message, from_email, [student.email])

    except Exception as e:
        logger.error(f"Error sending notification: {e}")



