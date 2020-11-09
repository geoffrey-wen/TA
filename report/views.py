from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Report, Tag, Collaboration, Images
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, AnonymousUser
from .filters import TagFilter
from django.db.models import Case, Value, When,IntegerField
import datetime
from django.contrib import messages
from user.models import PointHistory, CareerHistory


def About(request):
    return HttpResponse('LoremIpsum')

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    ordering = ['-date_reported__date','urgency','importance']
    paginate_by = 5

class UserReportListView(LoginRequiredMixin, ListView):
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
        if (not context['position']) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress__lte = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        return context

class UserTakenListView(LoginRequiredMixin, ListView):
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
        if (not context['position']) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress__lte = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        return context

class UserCollaborationListView(LoginRequiredMixin, ListView):
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
        if (not context['position']) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress__lte = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        return context

class UserCareerListView(LoginRequiredMixin, ListView):
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
        if (not context['position']) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        return context

class UserPointListView(LoginRequiredMixin, ListView):
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
        if (not context['position']) or (user.profile.level() > self.request.user.profile.level()):
            temp = []
            temp.append(user.profile.point())
            temp.append(user.report_set.count())
            temp.append(user.reporttaken_set.count())
            temp.append(user.reporttaken_set.filter(progress__lte = 3).count() + user.reporttaken_set.filter(progress__lte = 5).count())
            temp.append(user.reporttaken_set.filter(progress = 4).count())
            temp.append(user.reporttaken_set.filter(progress__gte = 6).count())
            context['stats'] = temp
        return context

class TagReportListView(LoginRequiredMixin, ListView):
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

    """
    def post(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, name=self.kwargs.get('tagname'))
        context['description'] = tag.description
        context['creator'] = tag.creator
        is_subscribed = self.request.user.profile in tag.subscriber_set.all()
        if "subscribeButton" in request.Post :
            if is_subscribed:
                remove user-tag relation
            else:
                add user-tag relation
            save change
        context['is_subscribed'] = self.request.user.profile in tag.subscriber_set.all()
        return return redirect('tag-reports')
    """


class SubscribedReportListView(LoginRequiredMixin, ListView):
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

#before change tag-report field to report model
"""
class TagReportListView(ListView):
    model = Report
    template_name = 'report/tag_reports.html'
    paginate_by = 5

    def get_queryset(self):
        tag = get_object_or_404(Tag, name=self.kwargs.get('tagname'))
        return tag.report.all().order_by('-date_reported')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, name=self.kwargs.get('ragname'))
        context['description'] = tag.description
        context['creator'] = tag.creator
        return context
"""

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = get_object_or_404(Report, pk=self.kwargs.get('pk'))
        context['collaborations'] = Collaboration.objects.filter(report = report).order_by('date')
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


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    fields = ['title', 'content', 'image', 'tag', 'urgency', 'importance']

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        return super().form_valid(form)

class ReportUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Report
    fields = ['title', 'content', 'image', 'tag', 'urgency', 'importance']

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        return  super().form_valid(form)

    def test_func(self):
        report = self.get_object()
        if self.request.user == report.reporter:
            return True
        return False

class ReportDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Report
    success_url = '/'

    def test_func(self):
        report = self.get_object()
        if self.request.user == report.reporter:
            return True
        return False

class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['name','description']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

def TagList(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    tags = Tag.objects.all()
    tag_count = tags.count()
    tag_filter = TagFilter(request.GET, queryset=tags)
    tags = tag_filter.qs

    context = {'tags':tags,
               'tag_count':tag_count,
               'tag_filter':tag_filter}
    return render(request, 'report/tag_list.html', context)

def ProgressTaken(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    user = request.user
    reports = Report.objects.filter(taker=user).order_by('urgency','importance', '-date_reported__date')
    reports_ongoing = reports.filter(progress__lte=3) | reports.filter(progress=5)
    reports_finished = reports.filter(progress__gte=6).order_by('-date_last_progress')
    reports_not_approved = reports.filter(progress=4).order_by('-date_last_progress')
    context = {'reports_ongoing' : reports_ongoing,
               'reports_finished' : reports_finished,
               'reports_not_approved' : reports_not_approved}
    return render(request, 'report/progress_taken.html', context)

def ProgressSubscribed(request):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

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
    context = {'reports_not_taken' : reports_not_taken,
               'reports_ongoing': reports_ongoing,
               'reports_finished' : reports_finished,
               'reports_not_approved' : reports_not_approved}
    return render(request, 'report/progress_subscribed.html', context)

# def ProgressList(request):
