from django.contrib import admin
# from unfold.admin import ModelAdmin, TabularInline
from .models import Author, Book, Category, Library, LibraryBook, BorrowRecord


class LibraryBookInlineView(admin.TabularInline):
    model = LibraryBook

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio', 'birth_date', 'death_date')

@admin.register(Category)
class CategoryView(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude')
    inlines = [LibraryBookInlineView]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'isbn', 'published_date', 'author', 'category', 'available_copies', 'total_copies')


admin.site.register(BorrowRecord)