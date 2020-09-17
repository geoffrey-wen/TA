from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .form import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Unit, Profile, CareerHistory
from django.http import HttpResponse
from django.contrib.auth.models import User
# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else :
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})
#register.html belum dibikin, cari di bootstrap

@login_required
def profile(request):
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

    context = {
        'u_form' : u_form,
        'p_form' : p_form,
    }

    return render(request, 'user/profile.html', context)

class UnitCreateView(LoginRequiredMixin, CreateView):
    model = Unit
    fields = ['name', 'superior']

    def form_valid(self, form):
        return super().form_valid(form)

def UnitDetail(request, pk):
    if not request.user.username:
        return redirect('/login/?next=%s' % request.path)

    unit = get_object_or_404(Unit, pk=pk)
    members = Profile.objects.filter(unit=unit)
    unitless_user = User.objects.filter(unit = None, profile__unit = None)
    loopless_unit = Unit.objects.exclude(pk = unit.pk)
    for sub in unit.subordinate_list():
        loopless_unit = loopless_unit.exclude(pk = sub.pk)
    member_histories = []
    for member in members:
        temp = CareerHistory.objects.filter(user = member.user)
        if temp:
            temp = temp.order_by('date_created').last()
        member_histories.append(temp)
    print(member_histories)


    if request.method == 'POST':
        superior_pk = int(request.POST.get('superior'))
        head_pk = int(request.POST.get('head'))
        member_list = request.POST.getlist("member[]")
        job_list = request.POST.getlist("job[]")

        new_superior = Unit.objects.get(pk = superior_pk)
        if (new_superior == unit) or (new_superior in unit.subordinate_list()):
            print("huyu")
            #message error
        elif new_superior != unit.superior:
            unit.superior = new_superior
            unit.save()
            #message success

        if unit.head.pk != head_pk:
            unit.head = User.objects.get(pk=head_pk)
            unit.save()
            #message_success
            #add history

        valid_member = []
        valid_job = []
        for i in range(len(member_list)):
            if (member_list[i] != '0') and (job_list[i] != ''):
                valid_member.append(User.objects.get(pk = int(member_list[i])).profile)
                valid_job.append(job_list[i])
            else:
                print('huyu')
                #message warning

        for member in members:
            if not member in valid_member:
                member.unit = None
                member.save()
                #message success
                #add history

        for member in valid_member:
            if not member in members:
                member.unit = unit
                member.save()
                #message success
                #add history
                #else, bila unit sama periksa careehhistory
                #bila tidak punya career history
                #atau bila job di career history berubah
                #add history

        return HttpResponse()

    context = { 'unit' : unit,
                'members' : members,
                'unitless_user' : unitless_user.order_by('username'),
                'loopless_unit' : loopless_unit.order_by('name')}
    return render(request, 'user/unit_detail.html', context)




