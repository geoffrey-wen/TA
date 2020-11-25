from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponseRedirect
from .models import Report, Tag, Collaboration
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .filters import TagFilter
from django.db.models import Case, Value, When,IntegerField, Count
from django.db.models.functions import TruncWeek
import datetime
from datetime import timedelta
from django.contrib import messages
from user.models import PointHistory, CareerHistory, Auth


def auth_test(user, featurenum):
    if user.is_superuser:
        return True

    qs = Auth.objects.filter(feature = featurenum)
    if qs:
        qsuser = qs.exclude(auth_user = None)
        qsunit = qs.exclude(auth_unit = None)
        qslevel = qs.exclude(auth_level = None)

        auth_user = user in [auth.auth_user for auth in qsuser]

        if user.profile.unit:
            unit = user.profile.unit
        else:
            try:
                unit = user.unit
            except:
                unit = None
        auth_unit = unit in [auth.auth_unit for auth in qsunit]

        try:
            level = user.profile.level()
        except:
            level = None
        auth_level = level in [auth.auth_level for auth in qslevel]

        return auth_user or auth_unit or auth_level
    else:
        return True

def auth_template(user):
    auth_test_list = [auth_test(user, feature.value) for feature in Auth.Feature]

    template_test ={'left_navbar':{'subscribed': auth_test_list[1],
                                   'progress': auth_test_list[3]},
                    'report':{'create_a_report': auth_test_list[0],
                              'all_reports': auth_test_list[1],
                              'subscribed_reports': auth_test_list[1]},
                    'tag':{'create_a_tag': auth_test_list[2],
                           'all_tags': auth_test_list[0] or auth_test_list[1] or auth_test_list[2]},
                    'progress':{'progress_taken': auth_test_list[3],
                                'progress_subscribed': auth_test_list[3]},
                    'organization':{'create_a_unit': auth_test_list[5],
                                    'unit_hierarchy': auth_test_list[5],
                                    'all_users': auth_test_list[5],
                                    'manage_authorization': auth_test_list[6],
                                    'create_a_point_log': auth_test_list[7],
                                    'all_point_logs': auth_test_list[7]}
                    }
    return_dict = {'auth_test_list': auth_test_list,
                   'template_test': template_test}
    return return_dict


def About(request):
    signed_in_user = request.user
    context = {'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'report/about.html', context)


class ReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    ordering = ['-date_reported__date','urgency','importance']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def test_func(self):
        return auth_test(self.request.user, 2)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class UserReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    template_name = 'report/user_reports.html'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Report.objects.filter(reporter=user).order_by('-date_reported__date','urgency','importance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['selected_user'] = user
        context['position'] = CareerHistory.objects.filter(user = user).filter(date_ended = None)
        if (not context['position']) or (self.request.user == user ) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        signed_in_user = self.request.user
        test_dict = auth_template(signed_in_user)
        context['template_test'] = test_dict['template_test']
        if user == self.request.user:
            context['feature_test'] = [True for i in Auth.Feature]
        else :
            context['feature_test'] = test_dict['auth_test_list']
        return context

    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return True
        return auth_test(self.request.user, 5) or auth_test(self.request.user, 2)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class UserTakenListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    template_name = 'report/user_taken.html'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Report.objects.filter(taker=user).order_by('-date_last_progress__date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['selected_user'] = user
        context['position'] = CareerHistory.objects.filter(user = user).filter(date_ended = None)
        if (not context['position']) or (self.request.user == user ) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        signed_in_user = self.request.user
        test_dict = auth_template(signed_in_user)
        context['template_test'] = test_dict['template_test']
        if user == self.request.user:
            context['feature_test'] = [True for i in Auth.Feature]
        else :
            context['feature_test'] = test_dict['auth_test_list']
        return context

    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return True
        return auth_test(self.request.user, 5) or auth_test(self.request.user, 4)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class UserCollaborationListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Collaboration
    template_name = 'report/user_collab.html'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Collaboration.objects.filter(collaborator=user).order_by('-date__date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['selected_user'] = user
        context['position'] = CareerHistory.objects.filter(user = user).filter(date_ended = None)
        if (not context['position']) or (self.request.user == user ) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        signed_in_user = self.request.user
        test_dict = auth_template(signed_in_user)
        context['template_test'] = test_dict['template_test']
        if user == self.request.user:
            context['feature_test'] = [True for i in Auth.Feature]
        else :
            context['feature_test'] = test_dict['auth_test_list']
        return context

    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return True
        return auth_test(self.request.user, 5) or auth_test(self.request.user, 2)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class UserCareerListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CareerHistory
    template_name = 'report/user_career.html'
    paginate_by = 20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        queryset = CareerHistory.objects.filter(user = user)
        queryset = queryset.annotate(
            incumbent = Case(
                When(date_ended=None, then=Value(1)),
                default = 0,
                output_field=IntegerField()
            )
        ).order_by('-incumbent','-date_started')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['selected_user'] = user
        context['position'] = CareerHistory.objects.filter(user = user).filter(date_ended = None)
        if (not context['position']) or (self.request.user == user ) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        signed_in_user = self.request.user
        test_dict = auth_template(signed_in_user)
        context['template_test'] = test_dict['template_test']
        if user == self.request.user:
            context['feature_test'] = [True for i in Auth.Feature]
        else :
            context['feature_test'] = test_dict['auth_test_list']
        return context

    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return True
        return auth_test(self.request.user, 5) or auth_test(self.request.user, 6)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class UserPointListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = PointHistory
    template_name = 'report/user_point.html'
    paginate_by = 20

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return PointHistory.objects.filter(user = user).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['selected_user'] = user
        context['position'] = CareerHistory.objects.filter(user = user).filter(date_ended = None)
        if (not context['position']) or (self.request.user == user ) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        signed_in_user = self.request.user
        test_dict = auth_template(signed_in_user)
        context['template_test'] = test_dict['template_test']
        if user == self.request.user:
            context['feature_test'] = [True for i in Auth.Feature]
        else :
            context['feature_test'] = test_dict['auth_test_list']
        return context

    def test_func(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        if user == self.request.user:
            return True
        return auth_test(self.request.user, 5) or auth_test(self.request.user, 8)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class TagReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    template_name = 'report/tag_reports.html'
    paginate_by = 5

    def get_queryset(self):
        tag = get_object_or_404(Tag, name=self.kwargs.get('tagname'))
        return Report.objects.filter(tag=tag).order_by('-date_reported__date','urgency','importance')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, name=self.kwargs.get('tagname'))
        context['description'] = tag.description
        context['creator'] = tag.creator
        context['is_subscribed'] = self.request.user.profile in tag.subscriber_set.all()
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def post(self, request, *args, **kwargs):
        tag = get_object_or_404(Tag, name=self.kwargs.get('tagname'))
        profile = self.request.user.profile
        is_subscribed = profile in tag.subscriber_set.all()
        if "subscribeButton" in request.POST :
            if is_subscribed:
                profile.tag.remove(tag)
            else:
                profile.tag.add(tag)
        return redirect('tag-reports', tagname = tag.name)

    def test_func(self):
        return auth_test(self.request.user, 3) or auth_test(self.request.user, 2)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class SubscribedReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Report
    template_name = 'report/subscribed_report.html'
    paginate_by = 5

    def get_queryset(self):
        tags = self.request.user.profile.tag.all()
        queryset = Report.objects.none()
        for i in range(tags.count()):
            queryset = queryset | Report.objects.filter(tag=tags[i])
            #.union hanya works di terminal; why?
        queryset = queryset.distinct()
        #bikin attribute baru berdasarkan takernya
        queryset = queryset.annotate(
            taken_status = Case(
                When(taker=None, then=Value(0)),
                default = 1,
                output_field=IntegerField()
            )
        ).order_by('taken_status','-date_reported__date','urgency','importance')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def test_func(self):
        return auth_test(self.request.user, 2)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return HttpResponseRedirect(reverse('user-reports', kwargs={'username': self.request.user.username}))


class ReportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = get_object_or_404(Report, pk=self.kwargs.get('pk'))
        context['collaborations'] = Collaboration.objects.filter(report = report).order_by('date')
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        context['feature_test'] = auth_template(signed_in_user)['auth_test_list']
        return context

    def post(self, request, *args, **kwargs):
        report = get_object_or_404(Report, pk=self.kwargs.get('pk'))
        user = self.request.user
        if request.POST.get('takeButton') == 'True' :
            report.taker = user
            report.progress = 1
            report.date_last_progress = datetime.datetime.now()
            report.save()
        elif request.POST.get('collab'):
            if request.POST.get('new-subject') and request.POST.get('new-content'):
                try:
                    isimage = request.FILES['new-image']
                except:
                    isimage = False
                if isimage:
                    Collaboration.objects.create(
                        report = report,
                        subject = request.POST.get('new-subject'),
                        content = request.POST.get('new-content'),
                        collaborator = user,
                        image = request.FILES['new-image']
                    )
                else:
                    Collaboration.objects.create(
                        report = report,
                        subject = request.POST.get('new-subject'),
                        content = request.POST.get('new-content'),
                        collaborator = user
                    )
                messages.success(request, f"A new collaboration has been made")
            else:
                if request.POST.get('new-subject'):
                    messages.error(request, f"Please fill the content section !")
                elif request.POST.get('new-content'):
                    messages.error(request, f"Please fill the subject section !")
        elif request.POST.get('collab-del'):
            temp = int(request.POST.get('collab-del'))
            temp = Collaboration.objects.get(pk = temp)
            temp.delete()
            messages.success(request, f"A collaboration has been deleted")
        elif request.POST.get('progress'):
            report.progress = int(request.POST.get('progress'))
            report.progress_note = request.POST.get('progress-note')
            if request.POST.get('point') == "":
                messages.error(request, f"Please fill the point section !")
            elif request.POST.get('point'):
                report.point = int(request.POST.get('point'))
                PointHistory.objects.create(
                    user= report.reporter,
                    point= int(request.POST.get('point')),
                    note= f'Point from report: "{report.title}", pk = {report.pk}',
                    writer= user,
                )
            report.date_last_progress = datetime.datetime.now()
            report.save()
        return redirect('report-detail', pk = report.pk)

    def test_func(self):
        report = get_object_or_404(Report, pk=self.kwargs.get('pk'))
        if report.reporter == self.request.user:
            return True
        return auth_test(self.request.user, 2)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class ReportCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Report
    fields = ['title', 'content', 'image', 'tag', 'urgency', 'importance']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return auth_test(self.request.user, 1)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class ReportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report
    fields = ['title', 'content', 'image', 'tag', 'urgency', 'importance']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        return  super().form_valid(form)

    def test_func(self):
        report = self.get_object()
        if report.taker:
            return False
        if self.request.user == report.reporter:
            return True
        return False

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class ReportDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Report
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def test_func(self):
        report = self.get_object()
        if report.taker and self.request.user == report.taker:
            return True
        elif not(report.taker) and self.request.user == report.reporter:
            return True
        return False

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


class TagCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Tag
    fields = ['name','description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        signed_in_user = self.request.user
        context['template_test'] = auth_template(signed_in_user)['template_test']
        return context

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return auth_test(self.request.user, 3)

    def handle_no_permission(self):
        if not self.request.user.username:
            return redirect('/login/?next=%s' % self.request.path)
        messages.error(self.request, f"Sorry you are not authorized !")
        return redirect('home')


def TagList(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not (auth_test(request.user, 3) or auth_test(request.user, 2) or auth_test(request.user, 1)):
        messages.error(request, f"Sorry you are not authorized !")
        return redirect('home')

    tags = Tag.objects.all()
    tag_count = tags.count()
    tag_filter = TagFilter(request.GET, queryset=tags)
#    tag_filter = TagFilter({'name': 'a', 'description': '', 'creator': ''}, queryset=tags)
    tags = tag_filter.qs

    signed_in_user = request.user

    context = {'tags':tags,
               'tag_count':tag_count,
               'tag_filter':tag_filter,
               'template_test' : auth_template(signed_in_user)['template_test']}
    return render(request, 'report/tag_list.html', context)


def ProgressTaken(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 4):
        messages.error(request, f"Sorry you are not authorized !")
        return redirect('home')

    user = request.user
    reports = Report.objects.filter(taker=user).order_by('urgency','importance', '-date_reported__date')
    reports_ongoing = reports.filter(progress__lte=3) | reports.filter(progress=5)
    reports_finished = reports.filter(progress__gte=6).order_by('-date_last_progress')
    reports_not_approved = reports.filter(progress=4).order_by('-date_last_progress')

    signed_in_user = request.user
    context = {'reports_ongoing' : reports_ongoing,
               'reports_finished' : reports_finished,
               'reports_not_approved' : reports_not_approved,
               'template_test' : auth_template(signed_in_user)['template_test']}
    return render(request, 'report/progress_taken.html', context)


def ProgressSubscribed(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    if not auth_test(request.user, 4):
        messages.error(request, f"Sorry you are not authorized !")
        return redirect('home')

    tags = request.user.profile.tag.all()
    reports = Report.objects.none()
    for i in range(tags.count()):
        reports = reports | Report.objects.filter(tag=tags[i])
        # .union hanya works sdi terminal; why?
    reports = reports.distinct().order_by('urgency','importance', '-date_reported__date')
    reports_not_taken = reports.filter(taker=None)
    reports_ongoing = reports.filter(progress__lte=3) | reports.filter(progress=5)
    reports_finished = reports.filter(progress__gte=6).order_by('-date_last_progress')
    reports_not_approved = reports.filter(progress=4).order_by('-date_last_progress')

    signed_in_user = request.user
    context = {'reports_not_taken' : reports_not_taken,
               'reports_ongoing': reports_ongoing,
               'reports_finished' : reports_finished,
               'reports_not_approved' : reports_not_approved,
               'template_test' : auth_template(signed_in_user)['template_test']}
    return render(request, 'report/progress_subscribed.html', context)

# def ProgressList(request):

def Dashboard(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)
    # ambil parameter get
    # bisa ubah time interval
    reports_reported = Report.objects.annotate(interval=TruncWeek('date_reported')
                                    ).values('interval'
                                    ).annotate(reported=Count('id')
                                    ).values('interval', 'reported')

    reports_taken = Report.objects.exclude(date_last_progress = None
                                 ).annotate(interval=TruncWeek('date_last_progress')
                                 ).values('interval'
                                 ).annotate(taken=Count('progress')
                                 ).values('interval', 'taken')

    reports_not_taken_yet = Report.objects.filter(progress=None
                                         ).annotate(interval=TruncWeek('date_reported')
                                         ).values('interval'
                                         ).annotate(not_taken_yet=Count('id')
                                         ).values('interval', 'not_taken_yet')

    reports_in_checking = Report.objects.filter(progress__lte=3
                                       ).annotate(interval=TruncWeek('date_reported')
                                       ).values('interval'
                                       ).annotate(in_checking=Count('id')
                                       ).values('interval', 'in_checking')

    reports_not_approved = Report.objects.filter(progress=4
                                        ).annotate(interval=TruncWeek('date_reported')
                                        ).values('interval'
                                        ).annotate(not_approved=Count('id')
                                        ).values('interval', 'not_approved')

    reports_on_progress = Report.objects.filter(progress=5
                                       ).annotate(interval=TruncWeek('date_reported')
                                       ).values('interval'
                                       ).annotate(on_progress=Count('id')
                                       ).values('interval', 'on_progress')

    reports_finished = Report.objects.filter(progress__gte=6
                                    ).annotate(interval=TruncWeek('date_reported')
                                    ).values('interval'
                                    ).annotate(finished=Count('id')
                                    ).values('interval', 'finished')

    intervals = []
    for report in reports_reported:
        intervals.append(report['interval'])
    for report in reports_taken:
        intervals.append(report['interval'])

    labels = [min(intervals)]
    temp = min(intervals)
    while temp < max(intervals):
        temp = temp + timedelta(days=7)
        labels.append(temp)

    data = {'reported' : [],
            'taken' : [],
            'not_taken_yet' : [],
            'in_checking' : [],
            'not_approved' : [],
            'on_progress' : [],
            'finished' : []}

    for label in labels:
        temp = 0
        for report in reports_reported:
            if label == report['interval']:
                temp = report['reported']
        if temp:
            data['reported'].append(temp)
        else:
            data['reported'].append(0)

        temp = 0
        for report in reports_taken:
            if label == report['interval']:
                temp = report['taken']
        if report['interval'] in labels:
            data['taken'].append(temp)
        else:
            data['taken'].append(0)

        temp = 0
        for report in reports_not_taken_yet:
            if label == report['interval']:
                temp = report['not_taken_yet']
        if report['interval'] in labels:
            data['not_taken_yet'].append(temp)
        else:
            data['not_taken_yet'].append(0)

        temp = 0
        for report in reports_in_checking:
            if label == report['interval']:
                temp = report['in_checking']
        if report['interval'] in labels:
            data['in_checking'].append(temp)
        else:
            data['in_checking'].append(0)

        temp = 0
        for report in reports_not_approved:
            if label == report['interval']:
                temp = report['not_approved']
        if report['interval'] in labels:
            data['not_approved'].append(temp)
        else:
            data['not_approved'].append(0)

        temp = 0
        for report in reports_on_progress:
            if label == report['interval']:
                temp = report['on_progress']
        if report['interval'] in labels:
            data['on_progress'].append(temp)
        else:
            data['on_progress'].append(0)

        temp = 0
        for report in reports_finished:
            if label == report['interval']:
                temp = report['finished']
        if report['interval'] in labels:
            data['finished'].append(temp)
        else:
            data['finished'].append(0)

    # print([label.strftime("%d %b %y") for label in labels])
    signed_in_user = request.user
    context = {'data' : data,
               'labels' : labels,
               'template_test': auth_template(signed_in_user)['template_test']}
    return render(request, 'report/dashboard.html', context)