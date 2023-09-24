import json
import re

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
            line_directions = Departure.objects.filter(station__name=station_name, line__number=line_number).values('line__direction').distinct()
            for direction in [l['line__direction'] for l in line_directions]:
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
    directions = request.GET.get('direction', 'Petershausen').split(',')
    period = request.GET.get('period', 'Hour')

    if period == 'Weekday':
        format_str = '%%w'
    elif period == 'Hour':
        format_str = '%%H'
    else:
        format_str = '%%w - %%H'

    query = f"""
SELECT
    strftime('{format_str}', d.planned) as hour,
    count(d.planned) as num_departures_planned,
    count(d.actual) as num_departures_actual,
    avg((julianday(d.actual) - julianday(d.planned)) * 24 * 60) as delay_mean
FROM myapp_departure d
INNER JOIN main.myapp_line l ON d.line_id = l.id
INNER JOIN main.myapp_station s ON s.id = d.station_id
WHERE s.name = %(station_name)s
AND l.number = %(line_number)s
AND l.direction IN %(line_directions)s
--AND (d.canceled OR datetime(d.actual) < datetime('now'))
GROUP BY hour"""

    results = execute_raw_query(query, {
        'station_name': station,
        'line_number': line,
        'line_directions': directions,
    })

    return HttpResponse(json.dumps(results, indent=4))


def execute_raw_query(sql, parameters=None):
    # transform parameters if needed
    # lists
    # for key, param in parameters.items():
    #     if isinstance(param, list):
    #         if isinstance(p[0], str):
    #             entries = [f"'{p}'" for p in param]
    #         else:
    #             entries = [f"{p}" for p in param]
    #         param = "(" + ",".join(entries) + ")"

    # sqlite apparently only supports lists as parameters, at least some versoins
    # so we construct a list of parameter values in the order they appear in the query
    values_list = []
    parameter_keys_regex = '(' + '|'.join(parameters.keys()) + ')'
    pattern = re.compile(r'%\(' + parameter_keys_regex + '\)s')

    # offset to compensate for replacing with strings of varying length
    offset = 0

    for match in re.finditer(pattern, sql):
        param = parameters[match.group(1)]
        start_idx = match.start() + offset
        end_idx = match.end() + offset

        if isinstance(param, list):
            # lists are handled separately
            values_list.extend(param)
            placeholders = ",".join(["%s" for _ in param])
            replace_str = "(" + placeholders + ")"
        else:
            values_list.append(param)
            replace_str = "%s"

        sql = sql[:start_idx] + replace_str + sql[end_idx:]
        offset += len(replace_str) - (end_idx - start_idx)

    with connection.cursor() as cursor:
        cursor.execute(sql, values_list)

        # construct a dict of results
        columns = [c[0] for c in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

    return results

def migrate(request):
    import django.core.management
    from datetime import datetime

    out_str = ""

    out_str += str(datetime.now()) + " running migrate<br>"
    django.core.management.execute_from_command_line(['manage.py', 'migrate'])
    out_str += str(datetime.now()) + " migrate finished<br>"

    out_str += str(datetime.now()) + " running collectstatic<br>"
    django.core.management.execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    out_str += str(datetime.now()) + " collectstatic finished<br>"

    out_str += str(datetime.now()) + " running createsuperuser<br>"
    django.core.management.execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
    out_str += str(datetime.now()) + " createsuperuser finished<br>"

    return HttpResponse(out_str)