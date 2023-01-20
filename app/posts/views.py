from rest_framework import status
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import LimitOffsetPagination

from .models import Tweet, Comment, StatusType
from .serializers import StatusTweetSerializer, TweetSerializer, CommentSerializer, StatusTypeSerializer
from .permissions import PostPermission


class PostPagePagination(PageNumberPagination):
    page_size = 3


class TweetViewSet(viewsets.ModelViewSet):
    """
    API для создания, получения, изменения и удаления твитов
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer
    permission_classes = [PostPermission, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['text', ]
    search_fields = ['text', ]
    ordering_fields = ['updated_at', 'created_at', ]
    pagination_class = LimitOffsetPagination

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     text = self.request.query_params.get('text')
    #     if text:
    #         queryset = queryset.filter(text__icontains=text)
    #     return queryset

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def leave_status(self, request, pk=None):
        serializer = StatusTweetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                profile=request.user.profile,
                tweet=self.get_object()
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreateApiView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        return super().get_queryset().filter(tweet_id=self.kwargs.get('tweet_id'))

    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            tweet_id=self.kwargs.get('tweet_id')
        )


class StatusViewSet(viewsets.ModelViewSet):
    queryset = StatusType.objects.all()
    serializer_class = StatusTypeSerializer
