from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from report.models import Tag
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum

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

    def get_absolute_url(self):
        return reverse('unit-detail', kwargs={'pk': self.pk})

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

    def superior_list(self):
        if self.level() != "loop error":
            temp = self
            superiorlist = []
            while temp.superior:
                superiorlist.append(temp.superior)
                temp = temp.superior
            superiorlist = [superiorlist[i-1] for i in range(len(superiorlist),0,-1)]
            return superiorlist

    def superior_print(self):
        if self.level() != "loop error":
            indent = "   "
            for superior in self.superior_list():
                print(indent*(superior.level() - 1) + superior.name)
            print(indent*(self.level() - 1) + self.name + " -→ self")
        else:
            print("loop error")

    def subordinate_list_recursive(self, lev, subordinate_list):
        if lev>=0 and lev<=30:
            subordinate_list.append(self)
            lev = lev + 1
            for sub in self.subordinate_set.all():
                sub.subordinate_list_recursive(lev, subordinate_list)
        else:
            print("loop error")

    def subordinate_list(self):
        if self.level() != "loop error":
            lev = 0
            subordinate_list = []
            for sub in self.subordinate_set.all():
                sub.subordinate_list_recursive(lev, subordinate_list)
            return subordinate_list

    def subordinate_print(self):
        if self.level() != "loop error":
            print(self.name + " -→ self")
            indent = "   "
            for sub in self.subordinate_list():
                print(indent * (sub.level() - self.level()) + sub.name)
        else:
            print("loop error")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    tag = models.ManyToManyField(Tag, related_name='subscriber_set')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, related_name='member_set')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def level(self):
        if self.unit:
            return self.unit.level() + 1
        else:
            if self.user.unit:
                return self.user.unit.level()
            else:
                return '-'

    def point(self):
        temp = PointHistory.objects.filter(user__pk=self.user.pk)
        if temp:
            return temp.aggregate(points=Sum('point'))['points']
        else:
            return 0



class CareerHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.CharField(max_length=100, null=True, blank=True)
    date_started = models.DateTimeField(null=True, blank=True)
    date_ended = models.DateTimeField(null=True, blank=True)
    #kalau date started dan ended sama, maka dihapus

    def __str__(self):
        if self.date_ended:
            return f'[ENDED] {self.user.username} | {self.unit.name} | {self.job} | {self.date_started.strftime("%d%b%y")} - {self.date_ended.strftime("%d%b%y")}'
        else:
            return f'[STILL] {self.user.username} | {self.unit.name} | {self.job} | {self.date_started.strftime("%d%b%y")}'

class Auth(models.Model):
    class Feature(models.IntegerChoices):
        create_a_report = 1
        view_reports = 2
        create_a_tag = 3
        take_a_report = 4
        view_profile_info = 5
        manage_organization = 6
        manage_authorization = 7
        manage_points = 8
        collaborate_on_a_report = 9

    feature = models.IntegerField(choices=Feature.choices, null=True)
    auth_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    auth_unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    auth_level = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.auth_user:
            return f'[USER] {self.auth_user.username}'
        elif self.auth_unit:
            return f'[UNIT] {self.auth_unit.name}'
        else:
            return f'[LEVEL] {self.auth_level}'

class PointHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    point = models.IntegerField(null=True)
    note = models.TextField(null=True)
    date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    writer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='writer')

    def get_absolute_url(self):
        return reverse('home')

