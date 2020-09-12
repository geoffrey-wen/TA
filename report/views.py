from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Report, Tag
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, AnonymousUser
from .filters import TagFilter

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
        """
        queryset = Report.objects.none()
        for tag in tags:
            queryset = queryset.union(Report.objects.filter(tag=tag))
        """
        queryset = Report.objects.none()
        for i in range(tags.count()):
            queryset = queryset | Report.objects.filter(tag=tags[i])
        queryset = queryset.distinct()

        return queryset.order_by('-date_reported__date','urgency','importance')

#qs1 = User.objects.get(username='uji1').profile.tag.all()
#qs2 = User.objects.get(username='adminTA').profile.tag.all()

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

    def post(self, request, *args, **kwargs):
        report = get_object_or_404(Report, pk=self.kwargs.get('pk'))
        user = self.request.user
        if request.POST.get('takeButton') == 'True' :
            report.taker = user
            report.progress = 1
            report.save()
        if request.POST.get('progress'):
            report.progress = int(request.POST.get('progress'))
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
    fields = ['title', 'content', 'image', 'tag']

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