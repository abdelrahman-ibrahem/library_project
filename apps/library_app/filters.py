import django_filters
from django.db.models import Q
from .models import * 



class LibraryFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name='library_books__book__category__name',
        lookup_expr='icontains',
        label='Category name'
    )
    

    author = django_filters.CharFilter(
        field_name='library_books__book__author__name',
        lookup_expr='icontains',
        label='Author name'
    )
    

    class Meta:
        model = Library
        fields = ['category', 'author',]

class AuthorFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name='books__category__name',
        lookup_expr='icontains',
        label='Filter by book category name'
    )
    
    library = django_filters.ModelChoiceFilter(
        field_name='books__librarybook__library',
        queryset=Library.objects.all(),
        label='Filter by library'
    )

    class Meta:
        model = Author
        fields = ['category', 'library']



class BookFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        field_name='category',
        queryset=Category.objects.all(),
        label='Category'
    )
    
    author = django_filters.ModelChoiceFilter(
        field_name='author',
        queryset=Author.objects.all(),
        label='Author'
    )
    
    library = django_filters.ModelChoiceFilter(
        field_name='librarybook__library',
        queryset=Library.objects.all(),
        label='Library',
        method='filter_by_library',
    )
    
    

    class Meta:
        model = Book
        fields = ['category', 'author', 'library']
    
    def filter_by_library(self, queryset, name, value):
        # Get books that are available in the selected library
        return queryset.filter(
            librarybook__library=value,
            librarybook__available_quantity__gt=0
        ).distinct()




class AuthorDetailsFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        field_name='books__category',
        queryset=Category.objects.all(),
        label='Category',
        method='filter_by_category'
    )
    
    library = django_filters.ModelChoiceFilter(
        field_name='books__librarybook__library',
        queryset=Library.objects.all(),
        label='Library',
        method='filter_by_library'
    )

    class Meta:
        model = Author
        fields = ['category', 'library']

    def filter_by_category(self, queryset, name, value):
        return queryset.filter(books__category=value).distinct()

    def filter_by_library(self, queryset, name, value):
        return queryset.filter(
            books__librarybook__library=value,
            books__librarybook__available_quantity__gt=0
        ).distinct()