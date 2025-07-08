from rest_framework import serializers
from .models import *
from apps.library_app.util.generic import get_author_books_count
from datetime import datetime, timedelta
from utils.generic import send_websocket_message


class LibrarySerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Library
        fields = '__all__'
        extra_fields = ['distance']

    def get_distance(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and hasattr(user, 'profile') and user.profile.latitude and user.profile.longitude:
            return obj.distance_from(float(user.profile.latitude), float(user.profile.longitude))
        return None

class AuthorSerializer(serializers.ModelSerializer):
    book_counts = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id',
            'name',
            'bio',
            'birth_date',
            'death_date',
            'book_counts',
        ]
    
    def get_book_counts(self, instance):
        return get_author_books_count(instance)


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'description',
            'author_name',
            'cover_image',
            'isbn',
            'published_date',
            'category_name',
            'total_copies',
            'available_copies'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', )

class BookDetailsSerialzer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'description',
            'cover_image',
            'isbn',
            'published_date',
            'total_copies',
            'available_copies',
            'category'
        ]


class AuthorDetailsSerializer(serializers.ModelSerializer):
    books = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'id',
            'name',
            'bio',
            'birth_date',
            'death_date',
            'books'
        ]
    
    def get_books(self, instance):
        books = instance.books.all()
        request = self.context.get('request')
        if request:
            category_id = request.query_params.get('category', '')
            library_id = request.query_params.get('library', '')
            
            if category_id:
                books = books.filter(category__pk=category_id)
            if library_id:
                books = books.filter(
                    librarybook__library__pk=library_id,
                    librarybook__available_quantity__gt=0
                ).distinct()
        return BookDetailsSerialzer(books, many=True).data

class BorrowRecordSerializer(serializers.Serializer):
    book_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of BookCopy IDs to be borrowed",
        min_length=1,
        max_length=3  # Maximum 3 books per transaction
    )
    due_date = serializers.DateField(
        help_text="Date when books should be returned (max 1 month from now)"
    )
    library_id = serializers.IntegerField(
        help_text="Library ID"
    )

    def validate_due_date(self, value):
        """
        Validate that the due date is not more than 1 month in the future
        """
        max_due_date = datetime.now().date() + timedelta(days=30)
        if value > max_due_date:
            raise serializers.ValidationError(
                "Maximum borrowing period is 1 month"
            )
        return value
    
    def validate_library_id(self, value):
        """
        Validate the library existance
        """
        if not Library.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Library is not found"
            )
        return value

    def validate_book_ids(self, value):
        """
        Validate that all book copies exist and are available
        """
        available_copies = Book.objects.filter(
            id__in=value,
            total_copies__gt=0
        ).values_list('id', flat=True)

        if len(available_copies) != len(value):
            unavailable_ids = set(value) - set(available_copies)
            raise serializers.ValidationError(
                f"The following book copies are not available: {unavailable_ids}"
            )
        return value

    def create(self, validated_data):
        """
        Create borrow records for each book copy
        """
        user = self.context['request'].user
        book_ids = validated_data['book_ids']
        due_date = validated_data['due_date']
        library_id = validated_data['library_id']

        library_obj = Library.objects.get(id=library_id)

        # Check if user already has 3 books borrowed
        active_borrows = BorrowRecord.objects.filter(
            user=user,
            is_returned=False
        ).count()
        
        if active_borrows + len(book_ids) > 3:
            raise serializers.ValidationError(
                f"You can only borrow up to 3 books at a time. "
                f"You currently have {active_borrows} books borrowed."
            )

        borrow_records = []
        for copy_id in book_ids:
            book_obj = Book.objects.get(id=copy_id)
            borrow_record = BorrowRecord.objects.create(
                user=user,
                book=book_obj,
                due_date=due_date,
                library=library_obj
            )
            borrow_records.append(borrow_record)
            
            # Update book copy status
            book_obj.available_copies = book_obj.available_copies - 1
            book_obj.save()
            object = library_obj.library_books.filter(book=book_obj).first()
            object.available_quantity = object.available_quantity - 1
            object.save()
            send_websocket_message(
                f"book_availability_{book_obj.id}",
                {
                    "type": "book_available",
                    "book_id": self,
                    "available_copies": book_obj.available_copies
                }
            )

        return borrow_records


class RecordSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username")
    library = serializers.CharField(source="library.name")
    book = serializers.CharField(source="book.title")
    borrow_date = serializers.DateTimeField(format="%Y-%m-%d")
    due_date = serializers.DateTimeField(format="%Y-%m-%d")
    return_date = serializers.DateTimeField(format="%Y-%m-%d", allow_null=True)
    
    class Meta:
        model = BorrowRecord
        fields = '__all__'