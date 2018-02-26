# this module implements an interface similar to django.utils.timezone
from datetime import datetime
from time import timezone


def now():
    return datetime.now(timezone.utc)
