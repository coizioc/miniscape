import datetime

from django.db import models


class Task(models.Model):
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=200)
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=False)
    start_time = models.DateTimeField(auto_now_add=True)
    completion_time = models.DateTimeField()
    guild = models.CharField(max_length=200)
    channel = models.CharField(max_length=200)

    # Extra Data should be a JSON-dumped string for extra info needed by certain tasks.
    # For example, runecrafting will add JSON like
    # { "item_id": 138, "item_name": "law rune", "quantity": 100, "len_minutes": 20, "is_pure": false }
    # And then that extra data will be parsed by the relevant code that uses the data
    extra_data = models.TextField()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.type} task for user {self.user.nick}. Extra data: {self.extra_data}"

    @property
    def is_completed(self):
        return self.completion_time < datetime.datetime.now(datetime.timezone.utc)
