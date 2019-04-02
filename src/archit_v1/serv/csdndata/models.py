# serv/csdndata/models.py
"""
"""

from django.db import models

from django.db.models import CharField, DateTimeField
# from django.db.models import ForeignKey
# from django.db.models import URLField
from django.db.models import IntegerField
# from django.db.models import BooleanField
# from django.db.models import EmailField

from datetime import datetime
# from django.utils import timezone
import pytz


class UserID(models.Model):
    user_id = CharField(max_length=64)
    register_date = DateTimeField(
        'user register date',
        default=datetime(1970, 1, 1, 0, 0, 0,
                         tzinfo=pytz.timezone('UTC')))
    # email = EmailField()
    # birthday

    name = CharField(max_length=64, default="")  # webname

    """here field just only for crawler priority"""
    visit = IntegerField(default=-1)
    rank = IntegerField(default=-1)

    def __str__(self):
        return self.user_id

    def __repr__(self):
        return "[{}] {}({})".format(id(self), self.name, self.user_id)
