from django.shortcuts import render

# Create your views here.
from django.shortcuts import Http404, get_object_or_404
from django.http import JsonResponse

import sys
import datetime

#####################################
# generic views
#####################################
from rest_framework import generics, mixins
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

#
# model
#
from ..models import UserID
from ..models import VisualData
from ..models import Fans, Follow
# serialize
from .serializers import UserIDSerializer
from .serializers import VisualDataSerialzier
from .serializers import FansSerializer, FollowSerializer


class UserIDViewCommonMixin():
    serializer_class = UserIDSerializer

    def get_queryset(self):
        return UserID.objects.all()


class UserIDList(UserIDViewCommonMixin, generics.ListCreateAPIView):
    def get_queryset(self):
        if self.request.GET.get("p"):
            try:
                page = int(self.request.GET.get("p"))
                idx_h = page * 50
                idx_e = (page + 1) * 50
                objs = UserID.objects.all()
                length = len(objs)
                if page >= 0:
                    if idx_h < length < idx_e:
                        return objs[idx_h:]
                    elif idx_h > length:
                        raise IndexError("out of range")
                    elif idx_e < length:
                        return objs[idx_h:idx_e]
                else: raise IndexError("not support negative yet")
            except IndexError as e:
                print(e, file=sys.stderr)
                raise Http404("{}".format(e))  # -[o] update to DRF response type later
        else:
            try:
                objs = super().get_queryset()
                if len(objs) <= 50:
                    return objs
                else:
                    return objs[:50]
            except ValueError as e:
                raise Http404("wrong index page")  # -[o] update to DRF response type later


class UserIDDetail(UserIDViewCommonMixin, mixins.UpdateModelMixin, generics.RetrieveDestroyAPIView):
    '''n/a'''

    def get_object(self):
        user_id = self.kwargs['user_id']
        try:
            # userid = self.get_queryset().filter(
            #     Q(user_id=user_id)).distinct()[0]
            userid = get_object_or_404(UserID, user_id=user_id)
        except KeyError:
            raise Http404("require user_id")  # -[o] update to DRF response type later
        return userid

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class FansList(generics.ListCreateAPIView):
    serializer_class = FansSerializer

    def get_queryset(self):
        _ = get_object_or_404(UserID, user_id=self.kwargs['user_id'])
        qs = Fans.objects.filter(fans_of=_.id)
        queryset = qs
        return queryset


class FansDetail(mixins.UpdateModelMixin, generics.RetrieveDestroyAPIView):
    serializer_class = FansSerializer

    def get_object(self):
        _ = get_object_or_404(UserID, user_id=self.kwargs['user_id'])
        fanses = _.fanses_set.all()
        try:
            idx = int(self.kwargs['fans_idx']) - 1
            fans = fanses[idx]
        except Exception as err:
            print(err, file=sys.stderr)
            raise Http404("out of index")
        return fans

    # def get(self, request, site, user_id, fans_idx):
    def get(self, request, user_id, fans_idx):
        try:
            data = FansSerializer(self.get_object()).data
        except Exception:
            raise
        return Response(data)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class FollowViewCommonMixin(object):
    serializer_class = FollowSerializer

    def get_queryset(self):
        _ = get_object_or_404(UserID, user_id=self.kwargs["user_id"])
        return _.follow_set.all()


class FollowList(FollowViewCommonMixin, generics.ListCreateAPIView):
    ''' n/a'''


class FollowDetail(FollowViewCommonMixin, generics.RetrieveDestroyAPIView):
    '''n/a '''

    def get_object(self):
        follows = super().get_queryset()

        try:
            idx = int(self.kwargs['follow_idx']) - 1
            follow = follows[idx]
        except Exception as err:
            print(err, file=sys.stderr)
            raise Http404("out of index")
        return follow


class VisualDataViewCommonMixin(object):
    serializer_class = VisualDataSerialzier

    def get_queryset(self):
        _ = get_object_or_404(UserID, user_id=self.kwargs["user_id"])
        return _.visualdata_set.all()


class VisualDataList(VisualDataViewCommonMixin, generics.ListCreateAPIView):
    ''' n/a'''


class VisualDataDetail(VisualDataViewCommonMixin, generics.RetrieveDestroyAPIView):
    '''n/a '''

    def get_object(self):
        try:
            visualdatas = super().get_queryset()
            filter_date = datetime.datetime.strptime(
                self.kwargs['date'], "%Y-%m-%d").date()
            qs = visualdatas.filter(crawlerDate__year=filter_date.year,
                                    crawlerDate__month=filter_date.month, )
            d = {_.crawlerDate.day: _ for _ in qs}
            return d[min(d.keys(), key=lambda _: abs(_ - filter_date.day))]
        except Exception as e:
            print(e, file=sys.stderr)
            raise Http404("{}".format(e))  # -[o] update to DRF response type later
