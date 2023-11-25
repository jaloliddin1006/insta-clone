from django.urls import path
from .views import BookListAPIView, BookDetailAPIView, BookDeleteAPIView, BookUpdateAPIView,\
    BookCreateAPIView, BookListCreateAPIView, BookUpdateDeleteAPIView, BookViewSet

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('books', BookViewSet, basename='book')


urlpatterns = [
    # path('books/', BookListAPIView.as_view(), name='book-list'),
    # path('books/list-create/', BookListCreateAPIView.as_view(), name='book-list-create'),
    # path('books/update-delete/<int:pk>/', BookUpdateDeleteAPIView.as_view(), name='book-update-delete'),
    # path('books/create/', BookCreateAPIView.as_view(), name='book-create'),
    # path('books/<int:pk>/', BookDetailAPIView.as_view(), name='book-detail'),
    # path('books/<int:pk>/delete/', BookDeleteAPIView.as_view(), name='book-delete'),
    # path('books/<int:pk>/update/', BookUpdateAPIView.as_view(), name='book-update'),

]

urlpatterns += router.urls