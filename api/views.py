from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ViewSetMixin

from .models import Comment, Follow, Group, Post, User
from .permissions import IsOwnerOrReadOnly
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['group']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    lookup_fields = ('post', 'id')

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        queryset = get_object_or_404(Post, id=self.kwargs.get('post_id')).comments
        return queryset


class GroupViewSet(ViewSetMixin, ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)


class FollowViewSet(ViewSetMixin, ListCreateAPIView):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ['=user__username', '=following__username']

    def perform_create(self, serializer):
        author_name = self.request.POST.get('following')
        try:
            author = User.objects.exclude(id=self.request.user.id).get(
                username=author_name
            )
        except User.DoesNotExist:
            raise PermissionDenied('Подписка не разрешена')
        serializer.save(user=self.request.user, following=author)
