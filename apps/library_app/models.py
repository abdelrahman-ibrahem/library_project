from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from geopy.distance import geodesic
from django.db.models import Q


def upload_book_cover_to(instance, filename):
    return f'books/{instance.isbn}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to=upload_book_cover_to, null=True, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, related_name='books', on_delete=models.CASCADE)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new book
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author.name}"

class Library(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

    def distance_from(self, user_lat, user_lon):
        if not all([self.latitude, self.longitude, user_lat, user_lon]):
            return None
        return geodesic((self.latitude, self.longitude), (user_lat, user_lon)).km

class LibraryBook(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='library_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('library', 'book')

class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def calculate_penalty(self):
        if not self.is_returned and datetime.now().date() > self.due_date:
            overdue_days = (datetime.now() - self.due_date).days
            return overdue_days * 10  # $10 per day penalty
        return 0.0

    def save(self, *args, **kwargs):
        if not self.is_returned:
            self.penalty_amount = self.calculate_penalty()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} borrowed {self.book.title}"