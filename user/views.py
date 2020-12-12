from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .form import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Unit, Profile, CareerHistory, Auth, PointHistory
from django.http import HttpResponse
from django.contrib.auth.models import User
import datetime
from .filters import UserFilter, PointHistoryFilter
from django.db.models import Sum
from report.views import auth_test, auth_template


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'user/register.html', {'form': form})


def profile(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    signed_in_user = request.user
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'template_test': auth_template(signed_in_user)['template_test']
    }

    return render(request, 'user/profile.html', context)


class UnitCreateView(LoginRequiredMixin,  UserPassesTestMixin, CreateView):
    model = Unit
    fields = ['name', 'superior']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def test_func(self):
        return auth_test(self.request.user, 6)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized to access unit-create!")
        return redirect('home')


def UnitDetail(request, pk):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 6):
        messages.error(request, f"Sorry you are not authorized to access unit-detail!")
        return redirect('home')

    unit = get_object_or_404(Unit, pk=pk)
    members = Profile.objects.filter(unit=unit)
    unitless_user = User.objects.filter(unit = None, profile__unit = None)
    loopless_unit = Unit.objects.exclude(pk = unit.pk)
    for sub in unit.subordinate_list():
        loopless_unit = loopless_unit.exclude(pk = sub.pk)
    member_histories = []
    for member in members:
        temp = CareerHistory.objects.filter(user = member.user)
        temp = temp.order_by('date_started').last()
        member_histories.append(temp)

    if request.method == 'POST':
        if unit.level() > 1:
            superior_pk = int(request.POST.get('superior'))
        head_pk = int(request.POST.get('head'))
        member_list = request.POST.getlist("member[]")
        job_list = request.POST.getlist("job[]")

        if unit.level() > 1:
            new_superior = Unit.objects.get(pk = superior_pk)
            if (new_superior == unit) or (new_superior in unit.subordinate_list()):
                messages.error(request, f"{new_superior.name} can't be added as Superior ")
            elif new_superior != unit.superior:
                unit.superior = new_superior
                unit.save()
                messages.success(request, f"{new_superior.name} has been set as {unit.name} superior")

        if head_pk:
            new_head = User.objects.get(pk=head_pk)
            if unit.head != new_head:
                if unit.head:
                    former_head = unit.head
                    temp = former_head.careerhistory_set.last()
                    temp.date_ended = datetime.datetime.now()
                    temp.save()
                    messages.success(request, f"{former_head.username} has been removed from {unit.name}")
                unit.head = new_head
                unit.save()
                CareerHistory.objects.create(
                    user=new_head,
                    unit=unit,
                    job='Head',
                    date_started=datetime.datetime.now()
                )
                messages.success(request, f"{new_head.username} has been set as head of {unit.name}")
        else:
            messages.error(request, f"Please set the head of {unit.name} ")

        valid_member = []
        valid_job = []
        for i in range(len(member_list)):
            if (member_list[i] != '0') and (job_list[i] != ''):
                temp = User.objects.get(pk = int(member_list[i])).profile
                if (temp in valid_member) or (temp.pk == head_pk):
                    messages.warning(request, f"There is duplicate of {temp.user.username}")
                else:
                    valid_member.append(temp)
                    valid_job.append(job_list[i])
            else:
                if member_list[i] == '0' and job_list[i] != '':
                    messages.warning(request, f"There is no user for {job_list[i]}")
                if member_list[i] != '0' and job_list[i] == '':
                    messages.warning(request, f"There is no job for {User.objects.get(pk = int(member_list[i])).username}")

        for member in members:
            if not member in valid_member:
                member.unit = None
                member.save()
                temp = CareerHistory.objects.filter(user=member.user).last()
                temp.date_ended = datetime.datetime.now()
                temp.save()
                messages.success(request, f"{member.user.username} has been removed from {unit.name}")
            else :
                index = valid_member.index(member)
                temp = member.user.careerhistory_set.last()
                if valid_job[index] != temp.job:
                    temp.date_ended = datetime.datetime.now()
                    temp.save()
                    CareerHistory.objects.create(
                        user = member.user,
                        unit = unit,
                        job = valid_job[index],
                        date_started = datetime.datetime.now()
                    )
                    messages.success(request, f"{member.user.username}'s job has been changed from {temp.job} to {valid_job[index]}")

        for i in range(len(valid_member)):
            if not valid_member[i] in members:
                valid_member[i].unit = unit
                valid_member[i].save()
                CareerHistory.objects.create(
                    user = valid_member[i].user,
                    unit = unit,
                    job = valid_job[i],
                    date_started = datetime.datetime.now()
                )
                messages.success(request, f"{valid_member[i].user.username} has been added to {unit.name}")

        return HttpResponse()

    signed_in_user = request.user
    context = { 'unit' : unit,
                'members' : members,
                'unitless_user' : unitless_user.order_by('username'),
                'loopless_unit' : loopless_unit.order_by('name'),
                'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'user/unit_detail.html', context)


def UnitHierarchy(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 6):
        messages.error(request, f"Sorry you are not authorized to access unit-list!")
        return redirect('home')

    units = Unit.objects.all()
    top_units = []
    for unit in units:
        if unit.level() == 1:
            top_units.append(unit)

    signed_in_user = request.user
    context = { 'top_units' : top_units,
                'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'user/unit_list.html', context)


def AuthDetail(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 7):
        messages.error(request, f"Sorry you are not authorized to access auth-detail!")
        return redirect('home')

    auth_list = []
    for feature in list(Auth.Feature):
        temp = [feature]
        temp.append(Auth.objects.filter(feature = feature.value).exclude(auth_user = None))
        temp.append(Auth.objects.filter(feature = feature.value).exclude(auth_unit = None))
        temp.append(Auth.objects.filter(feature = feature.value).exclude(auth_level = None))
        auth_list.append(temp)

    users = User.objects.all()
    units = Unit.objects.all()
    levels = list(set([unit.level() for unit in units]))
    levels.append(max(levels)+1)

    if request.method == 'POST':
        post_data = []
        for i in range(len(auth_list)):
            temp = []
            temp.append(request.POST.getlist(f"user{i+1}[]"))
            temp.append(request.POST.getlist(f"unit{i+1}[]"))
            temp.append(request.POST.getlist(f"level{i+1}[]"))
            post_data.append(temp)

        for i in range(len(auth_list)):
            for j in range(3):
                for item in auth_list[i][j+1]:
                    if j == 0:
                        if not str(item.auth_user.pk) in post_data[i][j]:
                            temp = item.auth_user
                            item.delete()
                            messages.success(request, f"{temp}'s \"{auth_list[i][0].label}\" authorization has been revoked!")
                    if j == 1:
                        if not str(item.auth_unit.pk) in post_data[i][j]:
                            temp = item.auth_unit
                            item.delete()
                            messages.success(request, f"{temp}'s \"{auth_list[i][0].label}\" authorization has been revoked!")
                    if j == 2:
                        if not str(item.auth_level) in post_data[i][j]:
                            temp = item.auth_level
                            item.delete()
                            messages.success(request, f"Level {temp} users' \"{auth_list[i][0].label}\" authorization has been revoked!")
                for datum in post_data[i][j]:
                    if j == 0 and datum != '0':
                        if not auth_list[i][j+1].filter(auth_user__pk = datum):
                            temp = User.objects.get(pk = datum)
                            Auth.objects.create(
                                feature = i+1,
                                auth_user = temp
                            )
                            messages.success(request, f"\"{auth_list[i][0].label}\" authorization has been given to {temp.username}!")
                    if j == 1 and datum != '0':
                        if not auth_list[i][j+1].filter(auth_unit__pk = datum):
                            temp = Unit.objects.get(pk=datum)
                            Auth.objects.create(
                                feature = i+1,
                                auth_unit = temp
                            )
                            messages.success(request, f"\"{auth_list[i][0].label}\" authorization has been given to {temp.name}!")
                    if j == 2 and datum != '0':
                        if not auth_list[i][j+1].filter(auth_level = datum):
                            Auth.objects.create(
                                feature = i+1,
                                auth_level = datum
                            )
                            messages.success(request, f"\"{auth_list[i][0].label}\" authorization has been given to level {datum} users !")
        return HttpResponse()

    signed_in_user = request.user
    context = {'auth_list' : auth_list,
               'users' : users,
               'units' : units,
               'levels' : levels,
               'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'user/auth_detail.html', context)


class PointHistoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = PointHistory
    fields = ['user', 'point', 'note']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def form_valid(self, form):
        form.instance.writer = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return auth_test(self.request.user, 8)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized to access point-create!")
        return redirect('home')


def UserList(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 6):
        messages.error(request, f"Sorry you are not authorized to access user-list!")
        return redirect('home')

    users = User.objects.all()
    user_filter = UserFilter(request.GET, queryset=users)
    users = user_filter.qs

    keyworduname = str(user_filter.form).split('<input')[1].split('"')[5]
    keywordunit = str(user_filter.form).split('<input')[2].split('"')[5]
    keywordjob = str(user_filter.form).split('<input')[3].split('"')[5]
    if not keywordunit == "id_unit":
        qs = User.objects.filter(unit__name__icontains = keywordunit)
        if not keyworduname == "id_username":
            qs = qs.filter(username__icontains=keyworduname)
        if not keywordjob == "id_job":
            qs = qs.filter(careerhistory__job__icontains = keywordjob)
        users = users|qs
    users = users.distinct()

    signed_in_user = request.user
    context = {'users':users,
               'user_filter':user_filter,
               'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'user/user_list.html', context)


def PointHistoryList(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 8):
        messages.error(request, f"Sorry you are not authorized to access point-list!")
        return redirect('home')

    point_logs = PointHistory.objects.all()
    point_log_filter = PointHistoryFilter(request.GET, queryset=point_logs)
    point_logs = point_log_filter.qs
    point_logs = point_logs.distinct()
    logs_sum = point_logs.aggregate(points=Sum('point'))['points']
    logs_count = point_logs.count()

    signed_in_user = request.user
    context = {'point_logs': point_logs.order_by('-date'),
               'point_log_filter': point_log_filter,
               'logs_sum' :logs_sum,
               'logs_count' : logs_count,
               'filter_data' : request.GET,
               'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'user/pointhistory_list.html', context)
