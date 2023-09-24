import json

from django.http import HttpResponse
from django.shortcuts import render
from django.db import connection

from .mvv_query import *
from .models import *

# Create your views here.
def run(request):
    watchers = Watcher.objects.all()

    for watcher in watchers:
        if watcher.provider == 'mvv':
            mvv_query(watcher)
        else:
            print(f'unknown watcher type {watcher.provider}!')

    return HttpResponse('blub')

def unique(lst):
    return list(set(lst))

def evaluation(request):
    stations = Station.objects.values('name').distinct()
    lines = unique([l.number for l in Line.objects.all()])
    directions = unique([l.direction for l in Line.objects.all()])

    data = {}
    for station_name in [s['name'] for s in stations]:
        data[station_name] = {}
        line_numbers = Departure.objects.filter(station__name=station_name).values('line__number').distinct()
        # lines = Line.objects.filter(station__name=station['name']).values('number').distinct()
        for line_number in [l['line__number'] for l in line_numbers]:
            data[station_name][line_number] = []
            line_directions = Departure.objects.filter(station__name=station_name, line__number=line_number).values('line__number').distinct()
            for direction in directions:
                data[station_name][line_number].append(direction)


    # data = {
    #     'stations': stations,
    #     'lines': lines,
    #     'directions': directions
    # },
    return render(request, 'myapp/evaluation.html', {'data': json.dumps(data)})

def data(request):
    station = request.GET.get('station', 'Heimstetten')
    line = request.GET.get('line', 'S2')
    direction = request.GET.get('direction', 'Petershausen')

    query = """
SELECT
    strftime('%%H', d.planned) as hour,
    count(d.planned) as num_departures_planned,
    count(d.actual) as num_departures_actual,
    avg((julianday(d.actual) - julianday(d.planned)) * 24 * 60) as delay_mean
FROM myapp_departure d
INNER JOIN main.myapp_line l ON d.line_id = l.id
INNER JOIN main.myapp_station s ON s.id = d.station_id
WHERE s.name = %(station_name)s
AND l.number = %(line_number)s
AND l.direction = %(line_direction)s
AND (d.canceled OR datetime(d.actual) < datetime('now'))
GROUP BY hour"""

    results = execute_raw_query(query, {
        'station_name': station,
        'line_number': line,
        'line_direction': direction,
    })

    return HttpResponse(json.dumps(results, indent=4))


def execute_raw_query(sql, parameters=None):
    with connection.cursor() as cursor:
        cursor.execute(sql, parameters)

        # construct a dict of results
        columns = [c[0] for c in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    return results

def migrate(request):
    import django.core.management
    django.core.management.execute_from_command_line(['manage.py', 'migrate'])