from django.shortcuts import render, redirect
from .forms import FileForm, GroupForm
from .models import File, FileLock, Group, Checkin, Checkout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
import logging
from django.contrib import messages
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from datetime import timedelta
from .services import FileService, GroupService

logger = logging.getLogger(__name__) # files.views


@login_required
def home(request):
    file_service = FileService()
    files = file_service.home()
    if request.method == 'POST':
        bulkCheckin(request=request)
    return render(request, 'home.html', {'files':files})


@login_required
def bulkCheckin(request):
    selected_files_ids= request.POST.getlist('selected_files')
    file_service = FileService()
    file_service.set_user(request.user)
    try:
        file = file_service.bulkCheckin(selected_files_ids)
    except ValueError as e:
        messages.error(request, e)
        return redirect('home')
    

@login_required
def checkin(request, id):
        file_service = FileService()
        file_service.set_user(request.user)
        try:
            file = file_service.checkinFile(id)
        except ValueError as e:
            messages.error(request, e)
            return redirect('home')
        form = FileForm(instance=file) 
        if request.method == 'POST':
            file_service.checkoutFile(file)
            form = FileForm(request.POST, request.FILES, instance=file)
            if form.is_valid():
                form.save()
                return redirect('home')         
        return render(request, 'checkin.html', {'form': form, 'file':file})


def check_file_status(request, id):
    file_service = FileService()
    file = file_service.check_file_status(id)
    return JsonResponse({'is_free': file.is_free})


@login_required
def addFile(request):
    form = FileForm()
    if request.method == 'POST': 
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.owner = request.user
            form.save()
            return redirect('home')  
    return render(request, 'file_form.html', {'form': form})


@login_required
def downloadFile(request, id):
    file_service = FileService()
    response = file_service.downloadFile(id)
    return response

@login_required
def deleteFile(request, id):
    file = File.objects.get(id=id)
    if request.method == 'POST':
        file.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': file})

@login_required
def generateReport(request, id):
    file_service = FileService()
    response = file_service.generateReport(id)
    return response

@login_required
def groupCheckin(request, id):
    group_service = GroupService()
    group_service.set_user(request.user)
    try:
        group, files, users = group_service.groupCheckin(id)
    except ValueError as e:
        messages.error(request, e)
        return redirect('all-groups')
    form = GroupForm(instance=group)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            form.save()
            return redirect('all-groups')
    return render(request, 'group_checkin.html', {'group': group, 'files':files, 'users':users, 'form':form})

@login_required
def addGroup(request):
    form = GroupForm()
    if request.method == 'POST': 
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            form.save()
            return redirect('all-groups')  
    return render(request, 'group_form.html', {'form': form})

def allGroups(request):
    groups = Group.objects.all()
    return render(request, 'all_groups.html', {'groups': groups})



@login_required
def deleteGroup(request, id):
    group = Group.objects.get(id=id)
    if request.method == 'POST':
        files= group.file_set.all()
        if FileLock.objects.filter(file__in=files).exists():
            messages.success(request, 'Group has a checked in file')
            return redirect('all-groups')
        group.delete()
        return redirect('all-groups')
    return render(request, 'delete.html', {'obj': group})

@login_required
def search(request):
    if request.method == 'POST':
        searched = request.POST.get('searched')
        files = File.objects.filter(file__icontains=searched)
    return render (request, 'search.html', {'searched':searched, 'files':files})



def favicon_view(request):
    return HttpResponse("")