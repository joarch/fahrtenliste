from threading import Semaphore

from django.conf import settings
from django.db.models import Max

from fahrtenliste_main.einstellung import get_einstellung
from fahrtenliste_main.models import Fahrt

semaphore_fahrt_nr = Semaphore()


def get_next_fahrt_nr():
    semaphore_fahrt_nr.acquire()
    max = Fahrt.objects.all().aggregate(Max('fahrt_nr'))['fahrt_nr__max']
    max = max or 0
    next = int(max) + 1

    min_fahrt_nr = get_einstellung(settings.EINSTELLUNG_MIN_FAHRT_NR)
    if next < min_fahrt_nr:
        next = min_fahrt_nr

    semaphore_fahrt_nr.release()
    return next
