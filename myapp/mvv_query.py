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
            try: api_error = request.json()['error']
            except: api_error = 'no api error'
            raise Exception(f'API Error ({request.status_code}): {api_error}')

        data = request.json()

        departures = data['departures']

        # iterate through departures and remove duplicates due to line splitting (S1 Freising/Flughafen)
        for idx, d in enumerate(departures):
            matching = [
                i for i,p in enumerate(departures[:idx]) if
                p['line']['number'] == d['line']['number'] and
                p['line']['name'] == d['line']['name'] and
                p['station']['name'] == d['station']['name'] and
                p['track'] == d['track'] and
                p['departurePlanned'] == d['departurePlanned'] and
                p['departureLive'] == d['departureLive']
            ]

            if len(matching) > 0:
                i = matching[0]
                dep_new = sorted(list(set([departures[i]['line']['direction'], d['line']['direction']])))
                departures[i]['line']['direction'] = "/".join(dep_new)
                departures.pop(idx)


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
            else:
                actual_dt = datetime.strptime(departure['departureDate'] + ' ' + departure['departureLive'], datetime_format)
                canceled = False

                if actual_dt < request_time:
                    # disregard departues which have already happened, but are still returned from response
                    continue
                else:
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
                    'canceled': canceled,
                    'last_update': request_time,
                    'watcher': watcher
                }
            )

        ApiRun.objects.create(
            watcher=watcher,
            timestamp=request_time,
            status='success'
        ).save()

    except Exception as e:
        ApiRun.objects.create(
            watcher=watcher,
            timestamp=request_time,
            status='failed',
            error=str(e)
        ).save()

        raise(e)

    return True