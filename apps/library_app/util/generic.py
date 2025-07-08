from apps.library_app.models import * 
from django.db.models import Count, Q

def get_author_books_count(author, request=None):
    queryset = author.books.all()
    
    if request:
        # Apply the same filters from the request to the books count
        category = request.query_params.get('category')
        library = request.query_params.get('library')
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if library:
            queryset = queryset.filter(librarybook__library_id=library)
    
    return queryset.count()