import requests
import re
from .models import *
from datetime import datetime, timedelta
import time

def mvv_query(watcher: Watcher):
    request_time = datetime.now()

    try:
        # replace timestamp parameter
        new_timestamp = str(int(request_time.timestamp()))
        url = re.sub(r'timestamp=\d*', f'timestamp={new_timestamp}', watcher.url)

        request = requests.get(url)
        if request.status_code != 200:
            print(f"status {request.status_code} for request {url}")
            return False

        data = request.json()

        for departure in data['departures']:
            # only departures with track number (-> no SEV)
            if not departure['track']:
                continue

            station, _ = Station.objects.get_or_create(name=departure['station']['name'])
            line, _ = Line.objects.get_or_create(
                type=departure['line']['name'],
                number=departure['line']['number'],
                direction=departure['line']['direction'],
                icon=departure['line']['symbol']
            )

            datetime_format = '%Y%m%d %H:%M'
            planned_dt = datetime.strptime(departure['departureDate'] + ' ' + departure['departurePlanned'], datetime_format)

            if departure['departureLive'] == 'Halt entfällt':
                canceled = True
                actual_dt = None
            elif actual_dt < request_time:
                # disregard departues which have already happened, but are still returned from response
                continue
            else:
                canceled = False
                actual_dt = datetime.strptime(departure['departureDate'] + ' ' + departure['departureLive'], datetime_format)

                # if actual is more than 12 hours before planned, we assume there to be a dateshift
                if (actual_dt - planned_dt).total_seconds() < -1 * 12 * 60 * 60:
                    actual_dt = actual_dt + timedelta(days=1)

            # check if a departure with matching station, line type, number and direction and planned time exists
            Departure.objects.update_or_create(
                station=station,
                line=line,
                planned=planned_dt,
                defaults={
                    'actual': actual_dt,
                    'in_time': departure['inTime'],
                    'canceled': canceled
                }
            )

        ApiRun.objects.create(
            watcher=watcher,
            timestamp=runtime,
            status='success'
        ).save()

    except Exception as e:
        ApiRun.objects.create(
            watcher=watcher,
            timestamp=runtime,
            status='failed',
            error=str(e)
        ).save()

        raise(e)

    return True