from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from .views import CommentViewSet
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from rest_framework import routers

router = routers.SimpleRouter(trailing_slash=False)
router.register('', CommentViewSet)




urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'comments.views.home', name='home'),
    # url(r'^comments/', include('comments.foo.urls')),
    url(r'^$', CommentViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^new$', CommentViewSet.as_view({'post': 'create'})),
    url(r'^id/(?P<pk>\d+)$', CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    url(r'^count$', CommentViewSet.as_view({'post': 'count'})),
    url(r'^thread$', CommentViewSet.as_view({'get': 'thread'})),
    url(r'^demo$', TemplateView.as_view(template_name='index.html')),
    url(r'^test$', TemplateView.as_view(template_name='test.html')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
