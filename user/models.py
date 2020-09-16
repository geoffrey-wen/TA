from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from report.models import Tag
from django.utils import timezone


# Create your models here.
class Unit(models.Model):
    class Status(models.IntegerChoices):
        Inactive = 0
        Active = 1

    name = models.CharField(max_length=100, null=True)
    superior = models.ForeignKey("self", on_delete=models.SET_NULL, related_name='subordinate_set', null=True)
    head = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(default=timezone.now, null=True, blank=True)
    date_deactivated = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=1, null=True, blank=True)
    #boolean status active/inactive

    def __str__(self):
        return f'{self.name}'

    def level(self):
        lev = 1
        temp = self
        while temp.superior and lev < 30:
            lev += 1
            temp = temp.superior
        if lev < 30:
            return lev
        else:
            return "loop error"

    def superior_print(self):
        if self.level() != "loop error":
            temp = self
            superiorlist = []
            while temp.superior:
                superiorlist.append(temp.superior)
                temp = temp.superior
            indent = ""
            superiorlist.reverse()
            for superior in superiorlist:
                print(indent + superior.name)
                indent = indent + "   "
            print(indent + self.name)
        else:
            print("loop error")

    def subordinate_recursive(self, lev):
        if lev>=0 and lev<=30:
            indent = "   " * lev
            print(indent + self.name)
            lev = lev + 1
            for sub in self.subordinate_set.all():
                sub.subordinate_recursive(lev)
        else:
            print("loop error")


    def subordinate_print(self):
        if self.level() != "loop error":
            unit = self
            lev = 0
            unit.subordinate_recursive(lev)
        else:
            print("loop error")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    tag = models.ManyToManyField(Tag, related_name='subscriber_set')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class CareerHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.CharField(max_length=100, null=True, blank=True)
    date_started = models.DateTimeField(null=True, blank=True)
    date_ended = models.DateTimeField(null=True, blank=True)

