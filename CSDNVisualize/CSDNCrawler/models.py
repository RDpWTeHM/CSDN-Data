from django.db import models

# Create your models here.
from django.db.models import CharField, ForeignKey, DateTimeField, URLField
from django.db.models import IntegerField, EmailField, BooleanField

from datetime import datetime
from django.utils import timezone
import pytz


class UserID(models.Model):
    user_id = CharField(max_length=64)
    register_date = DateTimeField(
        'user register date',
        default=datetime(1970, 1, 1, 0, 0, 0,
                         tzinfo=pytz.timezone('UTC')))
    # email = EmailField()
    # birthday

    name = CharField(max_length=64, default="")

    """here field just only for crawler priority"""
    visit = IntegerField(default=-1)
    rank = IntegerField(default=-1)

    def __str__(self):
        return str(self.user_id)

    def __repr__(self):
        return self.name


class Article(models.Model):
    user_id = ForeignKey(UserID, on_delete=models.CASCADE)  # 注意 on_delete 的含义
    articleid = CharField(max_length=16)
    originality = BooleanField(default=True)
    title = CharField(max_length=128, default="None")
    pub_date = DateTimeField(
        'article date published',
        default=datetime(1970, 1, 1, 0, 0, 0))
    read_num = IntegerField(default=-1)
    comments_num = IntegerField(default=-1)

    def __str__(self):
        return "Article ID: " + self.articleid


class VisualData(models.Model):
    user_id = ForeignKey(UserID, on_delete=models.CASCADE)
    crawlerDate = DateTimeField('data crowler date', auto_now=True)

    originality = IntegerField(default=-1)  # 原创文章数量
    reprint = IntegerField(default=-1)  # 转发数量

    fans = IntegerField(default=-1)  # 粉丝数量
    follow = IntegerField(default=-1)  # 关注数量

    likes = IntegerField(default=-1)  # 总点赞数量
    comments = IntegerField(default=-1)  # 总评论数量
    csdnlevel = IntegerField(default=-1)  # 等级
    visitors = IntegerField(default=-1)  # 访问量
    intergration = IntegerField(default=-1)  # 积分
    rank = IntegerField(default=-1)  # 排名

    def __str__(self):
        return "userid: " + str(self.user_id)

    def __repr__(self):
        return "=" * 15 + '  user_id:  ' + '=' * 15 + '\n' + \
               ' ' * 15 + "{!s}\n".format(self.user_id) + \
               '-' * 42 + '\n' + \
               "\tcrawlerDate: {!s}\n".format(self.crawlerDate) + \
               "\toriginality: {}\n".format(self.originality) + \
               "\tfans: {}\n".format(self.fans) + \
               "\tlikes: {}\n".format(self.likes) + \
               "\tcomments: {}\n".format(self.comments) + \
               "\tcsdnlevel: {}\n".format(self.csdnlevel) + \
               "\tvisitors: {}\n".format(self.visitors) + \
               "\tintergration: {}\n".format(self.intergration) + \
               "\trank: {}\n".format(self.rank)

    def __eq__(self, other):
        if not isinstance(other, VisualData):
            return NotImplemented
        # 调整比较顺序可能改善性能 - 但是目前先不考虑
        return str(self.user_id) == str(other.user_id) and \
               self.originality == other.originality and \
               self.fans == other.fans and \
               self.likes == other.likes and \
               self.comments == other.comments and \
               self.csdnlevel == other.csdnlevel and \
               self.visitors == other.visitors and \
               self.intergration == other.intergration and \
               self.rank == other.rank


class Follows(models.Model):
    followed_by = ForeignKey(UserID, on_delete=models.CASCADE)
    crawledDate = DateTimeField('follows crawled date', default=timezone.now)
    follow_id = CharField(max_length=64)
    follow_name = CharField(max_length=64, default="")

    #
    # more information, maybe useful someday
    #
    current_total_follows_num = IntegerField(default=-1)

    def __eq__(self, other):
      if not isinstance(other, Follows):
        return NotImplemented
      return str(self.followed_by) == str(other.followed_by) and \
             self.follow_id == other.follow_id and \
             self.follow_name == other.follow_name

    def __str__(self):
        return "{} followed by {}".format(self.follow_id, self.followed_by)

    def __repr__(self):
        return "{!r}".format(dict(self.__dict__))


class BaseUserIDInfo(models.Model):
    user_id = models.CharField(max_length=128)
    name = models.CharField(max_length=512, default='')

    class Meta:
        abstract = True


class Fans(BaseUserIDInfo):
    fans_of = models.ForeignKey(
        UserID, related_name="fanses_set", on_delete=models.CASCADE)

    crawledDate = models.DateField('fans crawled date', auto_now=True)
    current_total_fans_num = IntegerField(default=-1)

    def __str__(self):
        return self.user_id  # BaseUserIDInfo.user_id

    def __repr__(self):
        return self.user_id + " in Fans table, fans of " + self.fans_of.user_id
