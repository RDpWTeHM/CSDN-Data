from django.shortcuts import render

# Create your views here.
from django.shortcuts import Http404, get_object_or_404
from django.http import JsonResponse

import sys


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
from ..models import Fans
# serialize
from .serializers import FansSerializer


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
