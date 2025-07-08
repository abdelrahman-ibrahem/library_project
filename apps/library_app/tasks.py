from celery import shared_task
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

@shared_task
def reminder_notification():
    """
    Send daily reminders for books due in the next 3 days
    """
    # Calculate the date range (today + 3 days)
    reminder_start = datetime.now().date()
    reminder_end = reminder_start + timedelta(days=3)
    
    # Get all active borrow records due in the next 3 days
    records = BorrowRecord.objects.filter(
        is_returned=False,
        due_date__date__gte=reminder_start,
        due_date__date__lte=reminder_end
    ).select_related('user', 'book')
    
    for record in records:
        days_left = (record.due_date.date() - reminder_start).days
        subject = f"Reminder: Book '{record.book.title}' due in {days_left} day(s)"
        message = (
            f"Hello {record.user.username},\n\n"
            f"This is a reminder that your book '{record.book.title}' "
            f"is due on {record.due_date.strftime('%Y-%m-%d')}.\n\n"
            f"Please return it on time to avoid penalties.\n\n"
            f"Thank you,\n"
            f"The Library Team"
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [record.user.email],
            fail_silently=False,
        )