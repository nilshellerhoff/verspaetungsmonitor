from django.db.models import *


class Watcher(Model):
    provider = CharField(max_length=255)
    name = CharField(max_length=255)
    url = URLField(max_length=4096)

    def __str__(self):
        return self.provider + ' - ' + self.name


class ApiRun(Model):
    timestamp = DateTimeField()
    watcher = ForeignKey(Watcher, on_delete=SET_NULL, null=True)
    status = CharField(max_length=255)
    error = CharField(max_length=2048)

    def __str__(self):
        return str(self.timestamp) + ': ' + str(self.watcher)


class Station(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Line(Model):
    type = CharField(max_length=255)
    number = CharField(max_length=255)
    direction = CharField(max_length=255)
    icon = URLField()

    def __str__(self):
        return self.type + ' - ' + self.number + ' - ' + self.direction


class Departure(Model):
    station = ForeignKey(Station, on_delete=SET_NULL, null=True)
    line = ForeignKey(Line, on_delete=SET_NULL, null=True)
    planned = DateTimeField(max_length=255)
    actual = DateTimeField(max_length=255, null=True)
    in_time = BooleanField()
    canceled = BooleanField()

    def __str__(self):
        return str(self.planned) + ' - ' + self.station.name + ' - ' + self.line.number + ' ' + self.line.direction