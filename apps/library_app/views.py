import traceback
from rest_framework import generics, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from utils.generic import send_websocket_message
from utils.pagination import StandardResultsSetPagination
from rest_framework import viewsets
from datetime import datetime
from .serializers import *
from .models import *
from .filters import *

class ListLibraries(generics.ListAPIView):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LibraryFilter
    pagination_class = StandardResultsSetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ListAuthors(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilter
    pagination_class = StandardResultsSetPagination


class ListBooks(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    pagination_class = StandardResultsSetPagination


class ListAuthorDetails(generics.ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorDetailsFilter
    pagination_class = StandardResultsSetPagination

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context





class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "messages": serializer.errors
            })
        serializer.save()

        # Send confirmation email
        # send_borrow_confirmation_email.delay(user.email, book_copy.book.title, borrow_record.due_date)

        return Response(status=status.HTTP_201_CREATED)

    def return_books(self, request):
        books_ids = request.data.get('book_ids', [])
        records = BorrowRecord.objects.filter(user=request.user, book__id__in=books_ids, is_returned=False)

        if not records:
            return Response({
                "message": "There are not books borrowed"
            })
        for record in records:
            record.return_date = datetime.now()
            record.is_returned = True
            record.penalty_amount = record.calculate_penalty()
            record.save()
            # Update the current quantity
            record.book.available_copies = record.book.available_copies + 1
            record.book.save()
            object = record.library.library_books.filter(book=record.book).first()
            object.available_quantity = object.available_quantity + 1
            object.save()
            # notify with the updated count
            send_websocket_message(
                f"book_availability_{record.book.id}",
                {
                    "type": "book_available",
                    "book_id": record.book.id,
                    "available_copies": record.book.available_copies
                }
            )

        return Response({'statmessageus': 'book returned successfully'})
