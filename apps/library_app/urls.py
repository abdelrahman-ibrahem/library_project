from django.urls import path
from . import views

urlpatterns = [
    path('libraries/', views.ListLibraries.as_view(), name='library-list'),
    path('authors/', views.ListAuthors.as_view(), name='author-list'),
    path('books/', views.ListBooks.as_view(), name='books'),
    path('authors-details/', views.ListAuthorDetails.as_view(), name='authors-details'),
    path('books/borrow/', views.BorrowRecordViewSet.as_view({'post': 'create'})),
    path('books/borrow/return/', views.BorrowRecordViewSet.as_view({'post': 'return_books'})),
]