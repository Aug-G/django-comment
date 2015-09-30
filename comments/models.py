#coding=utf-8
from django.db import models
import time


class Thread(models.Model):
    uri = models.CharField('URI', max_length=256)
    title = models.CharField('标题', max_length=64)


class Comment(models.Model):
    thread = models.ForeignKey(Thread, verbose_name='Thread')
    parent = models.ForeignKey('self', verbose_name='Parent', null=True)
    created = models.DateTimeField('Created', auto_now_add=True)
    modified = models.DateTimeField('Modified', auto_now=True)
    mode = models.IntegerField('Mode', default=1, choices=((1, 'accepted'), (2, 'queue'), (3, 'deleted')))
    remote_addr = models.CharField('IP', max_length=32, null=True, blank=True )
    text = models.CharField('评论内容', max_length=256)
    author = models.CharField('作者', max_length=64, null=True, blank=True)
    email = models.CharField('电子邮件', max_length=64, null=True, blank=True)
    website = models.CharField('个人网站', max_length=64, null=True, blank=True)
    likes = models.IntegerField('赞成', default=0)
    dislikes = models.IntegerField('反对', default=0)


    def get_created_timestamp(self):
        try:
            return time.mktime(self.created.timetuple())
        except AttributeError:
            return ''

    def get_modified_timestamp(self):
        if self.modified is None:
            return None
        try:
            return time.mktime(self.modified.timetuple())
        except AttributeError:
            return None

