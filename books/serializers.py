from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'content', 'subtitle', 'author', 'isbn', 'price']

    ## hamma fieldlarni validate qilish uchun
    def validate(self, data):
        title = data.get('title')
        author = data.get('author')
        print(title, author)

        # if not title.isalpha():
        #     raise serializers.ValidationError({
        #         "status": "False",
        #         "message": "Title must be string"
        #     })

        if Book.objects.filter(title=title, author=author).exists():
            raise serializers.ValidationError({
                "status": "False",
                "message": "Book already exists"
            })
        return data

    ### faqat price fieldni validate qilish uchun
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError({
                "status": "False",
                "message": "Price must be greater than 0"
            })
        return value