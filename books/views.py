from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Book
from .serializers import BookSerializer
from rest_framework import generics, status


# class BookListAPIView(generics.ListAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

class BookListAPIView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        data = {
            "status": f"Returned {len(books)} books",
            "books": serializer.data
        }
        return Response(data)

# class BookDetailAPIView(generics.RetrieveAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

class BookDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.get(id=pk)
            serializer = BookSerializer(book)
            data = {
            "status": "Returned book",
            "book": serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response({"status": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

# class BookDeleteAPIView(generics.DestroyAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

class BookDeleteAPIView(APIView):
    def delete(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        book.delete()
        data = {
            "status": f"Deleted book with id {pk}"
        }
        return Response(data)


# class BookUpdateAPIView(generics.UpdateAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

class BookUpdateAPIView(APIView):
    def put(self, request, pk):
        book = get_object_or_404(Book, id=pk)
        serializer = BookSerializer(instance=book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "status": f"Updated book with id {pk}",
                "book": serializer.data
            }
            return Response(data)
        return Response(serializer.errors)

# class BookCreateAPIView(generics.CreateAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookSerializer

class BookCreateAPIView(APIView):
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data = {
                "status": "Created and saved new book",
                "book": serializer.data
            }
            return Response(data)
        return Response(serializer.errors)


class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

### viewsets
from rest_framework import viewsets

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_queryset(self):
        books = Book.objects.all()
        return books





## function based views
@api_view(['GET'])
def books_list_view(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)
