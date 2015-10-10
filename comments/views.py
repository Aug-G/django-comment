import json

from django.db.models import Count
from rest_framework import viewsets, status, exceptions, authentication
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import time

from .models import Comment, Thread
from .serializers import CommentSerializer
import utils
from utils.hash import sha1
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
from utils.textfilter import dfa_filter
from django.conf import settings


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    renderer_classes = (JSONRenderer, )
    authentication_classes = (authentication.BasicAuthentication, )

    def get_thread(self):
        uri = self.request.GET.get('uri')
        if not uri:
            raise exceptions.NotFound('uri not found')
        thread = Thread.objects.filter(uri=uri).first()
        if thread is None:
            thread = Thread(uri=uri, title=uri).save()
        return thread

    def create(self, request, *args, **kwargs):
        request.data['remote_addr'] = utils.anonymize(request.META.get('REMOTE_ADDR'))
        request.data['voters'] = utils.Bloomfilter(iterable=[request.META.get('REMOTE_ADDR')]).array
        self.thread = self.get_thread()
        response = super(CommentViewSet, self).create(request, *args, **kwargs)
        response.set_cookie(str(response.data['id']), sha1(response.data['text']))
        response.set_cookie('isso-%i' % response.data['id'], sha1(response.data['text']))

        message = RedisMessage(json.dumps(response.data))
        RedisPublisher(facility='thread-%i' % self.thread.pk, broadcast=True).publish_message(message)
        return response

    def perform_create(self, serializer):
        serializer.validated_data['text'] = dfa_filter.filter(serializer.validated_data.get('text'))
        serializer.validated_data['thread'] = self.thread
        serializer.save()

    def perform_update(self, serializer):
        serializer.validated_data['text'] = dfa_filter.filter(serializer.validated_data.get('text'))
        serializer.save()

    def list(self, request, *args, **kwargs):
        uri = request.GET.get('uri')
        root_id = request.GET.get('parent')
        nested_limit = request.GET.get('nested_limit', 0)
        after = request.GET.get('after', 0)
        queryset = self.get_queryset().filter(thread__uri=uri)
        limit  = request.GET.get('limit', 0)
        if after:
            after = time.localtime(float(after)+1)
            queryset = queryset.filter(created__gt=time.strftime("%Y-%m-%d %H:%M:%S", after))

        if root_id is not None:
            root_list = queryset.filter(parent=root_id)
        else:
            root_list = queryset.filter(parent__isnull=True)

        if limit:
            root_list = root_list[:limit]

        parent_count = queryset.values('parent').annotate(total=Count('parent'))
        reply_counts = {item['parent']: item['total'] for item in parent_count}
        if root_id is None:
            reply_counts[root_id] = queryset.filter(parent__isnull=True).count()
        else:
            root_id = int(root_id)

        rv = {
            'id': root_id,
            'total_replies': root_list.count(),
            'hidden_replies': reply_counts.get(root_id, 0) - root_list.count(),
            'replies': self.get_serializer(root_list, many=True).data
        }

        if root_id is None:
            for comment in rv['replies']:
                if comment['id'] in reply_counts:
                    comment['total_replies'] = reply_counts.get(comment['id'], 0)
                    replies = self.get_serializer(queryset.filter(parent=comment['id'])[:nested_limit], many=True).data
                else:
                    comment['total_replies'] = 0
                    replies = []

                comment['hidden_replies'] = comment['total_replies'] - len(replies)
                comment['replies'] = replies

        return Response(rv)

    def destroy(self, request, *args, **kwargs):
        id = request.COOKIES.get(str(self.kwargs.get('pk')), None)
        if id is None:
            raise  exceptions.NotAuthenticated
        instance = self.get_object()

        if self.get_queryset().filter(parent=instance.id).exists():
            instance.mode = 4
            instance.text = ''
            instance.author = ''
            instance.website = ''
            instance.save()
            response = Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)
        else:
            instance.delete()
            response = Response(None, status=status.HTTP_200_OK)

        response.delete_cookie(id)
        response.delete_cookie('isso-%s' % id)
        return response

    @list_route(methods=['get', 'post'])
    def count(self, request, *args, **kwargs):
        if request.method == 'GET':
            counts = self.get_queryset().filter(thread__uri=request.GET.get('uri')).count()
        else:
            counts = [self.get_queryset().filter(thread__uri=uri).count() for uri in request.data]
        return Response(counts)

    @list_route()
    def thread(self, request, *args, **kwargs):
        """
        Get thread websocket url
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        thread = self.get_thread()
        protocol = request.is_secure() and 'wss://' or 'ws://'
        url = protocol + request.get_host() + settings.WEBSOCKET_URL + 'thread-%i' % thread.id
        return Response(url)

    @detail_route(methods=['post'])
    def like(self, request, *args, **kwargs):
        comment = self.get_object()
        return Response(comment.vote(True, utils.anonymize(request.META.get('REMOTE_ADDR'))))

    @detail_route(methods=['post'])
    def dislike(self, request, *args, **kwargs):
        comment = self.get_object()
        return Response(comment.vote(False, utils.anonymize(request.META.get('REMOTE_ADDR'))))
