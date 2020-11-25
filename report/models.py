from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=35, unique=True)
    description = models.TextField(null=True)
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='tagcreated_set')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag-reports', kwargs={'tagname': self.name})


class Report(models.Model):

    class Level(models.IntegerChoices):
        HIGH = 1
        MEDIUM = 2
        LOW = 3

    class TaskLevel(models.IntegerChoices):
        Task_Taken = 1
        Field_Checking = 2
        Approved = 3
        Not_Approved = 4
        Responsing = 5
        Resolved = 6
        Postponed = 7
        Failed = 8


    title = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    date_reported = models.DateTimeField(default=timezone.now, null=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='report_images', null=True)
    tag = models.ManyToManyField(Tag)
    urgency = models.IntegerField(choices=Level.choices, null=True)
    importance = models.IntegerField(choices=Level.choices, null=True)
    progress = models.IntegerField(choices=TaskLevel.choices, null=True, blank=True)
    taker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reporttaken_set')
    date_last_progress = models.DateTimeField(null=True, blank=True)
    progress_note = models.TextField(null=True, blank=True)
    point = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('report-detail', kwargs={'pk': self.pk})


class Collaboration(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, null=True)
    content = models.TextField(null=True)
    date = models.DateTimeField(default=timezone.now, null=True)
    collaborator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='report_images', null=True, blank=True)


# class Images(models.Model):
#     report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
#     collaboration = models.ForeignKey(Collaboration, on_delete=models.CASCADE, null=True, blank=True)
#     image = models.ImageField(upload_to='report_images', null=True, blank=True)