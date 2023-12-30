from django.shortcuts import render, redirect
from .forms import FileForm, GroupForm
from .models import File, FileLock, Group, Checkin, Checkout
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib import messages
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from datetime import timedelta


def home(request):
    files = File.objects.all()
    if request.method == 'POST':
        bulkCheckin(request=request)
    return render(request, 'home.html', {'files':files})

def bulkCheckin(request):
    selected_files_ids= request.POST.getlist('selected_files')
    selected_files = File.objects.filter(id__in=selected_files_ids)
    locked_files = FileLock.objects.filter(file_id__in=selected_files)
    if locked_files.exists():
        # for lock in locked_files:
        #     if not lock.user == request.user:
                locked_file_names = [lock.file.file.name for lock in locked_files]
                messages.success(request, f"The following files are locked: {', '.join(locked_file_names)}")
                return redirect('home')
    else:
        print('1')
        for file in selected_files:
            lock_file(file, request.user)
            lock = FileLock.objects.get(file=file, user=request.user)
            file.is_free = False
            file.save()
            Checkin.objects.create(file=file, user=request.user)
            # Schedule the automatic check-out task after one hour
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=lock.locked_at + timedelta(seconds=15))
            task_name = f'files.tasks.automatic_check_out_{lock.id}' 
            mytask = PeriodicTask.objects.create(
                clocked=clocked,
                name=task_name,
                task='files.tasks.automatic_check_out',
                args=[lock.id],
                one_off=True
            )


def checkin(request, id):
        file = File.objects.get(id=id)
        form = FileForm(instance=file) 
        if request.method == 'POST':
            form = FileForm(request.POST, request.FILES, instance=file)
            lock = FileLock.objects.get(file=file, user=request.user)
            PeriodicTask.objects.filter(name=f'files.tasks.automatic_check_out_{lock.id}', args=[lock.id]).delete()
            unlock_file(file, request.user)
            file.is_free = True 
            file.save()
            c = Checkin.objects.filter(file=file, user=request.user).order_by('-created').first()
            Checkout.objects.create(checkin=c)
            if form.is_valid():
                form.save()
                return redirect('home')         
        if FileLock.objects.filter(file=file).exclude(user=request.user).exists():
            messages.success(request, 'File is checked in by another user')
            return redirect('home')
        if file.group is not None:
            if not file.group.users.filter(id=request.user.id).exists():
                messages.success(request, 'you can not checkin file in this group')
                return redirect('home')
        if not FileLock.objects.filter(file=file).exists():
            Checkin.objects.create(file=file, user=request.user)
            lock_file(file, request.user)
            lock = FileLock.objects.get(file=file, user=request.user)
            file.is_free = False
            file.save()
            # Schedule the automatic check-out task after one hour
            clocked, _ = ClockedSchedule.objects.get_or_create(clocked_time=lock.locked_at + timedelta(seconds=15))
            task_name = f'files.tasks.automatic_check_out_{lock.id}' 
            mytask = PeriodicTask.objects.create(
                clocked=clocked,
                name=task_name,
                task='files.tasks.automatic_check_out',
                args=[lock.id],
                one_off=True
            )
        return render(request, 'checkin.html', {'form': form, 'file':file})

def check_file_status(request, id):
    file = File.objects.get(id=id)
    return JsonResponse({'is_free': file.is_free})

def groupCheckin(request, id):
    group = Group.objects.get(id=id)
    files = group.file_set.all()
    users = group.users.all()
    form = GroupForm(instance=group)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if not form.is_valid():
            print(form.errors)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            form.save()
            return redirect('all-groups')
    return render(request, 'group_checkin.html', {'group': group, 'files':files, 'users':users, 'form':form})


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

    
@transaction.atomic 
def lock_file(file, user):
    FileLock.objects.create(file=file, user=user)

def unlock_file(file, user):
    FileLock.objects.filter(file=file, user=user).delete()

def downloadFile(request, id):
    file = File.objects.get(id=id)
    filename = file.file.name
    with open('media/{}'.format(filename), mode='rb') as f:
        file_contents = f.read()
    response = HttpResponse(file_contents, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'

    return response

def deleteFile(request, id):
    file = File.objects.get(id=id)
    if request.method == 'POST':
        file.delete()
        return redirect('home')
    return render(request, 'delete.html', {'obj': file})

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

def search(request):
    if request.method == 'POST':
        searched = request.POST.get('searched')
        files = File.objects.filter(file__icontains=searched)
    return render (request, 'search.html', {'searched':searched, 'files':files})

def generateReport(request, id):
    file = File.objects.get(id=id)
    checkins = Checkin.objects.filter(file=file)
    # Create the report content
    report_content = f"Check-in Report for File: {file}\n\n"
    for checkin in checkins:
        report_content += f"User: {checkin.user}\n"
        report_content += f"Check-in Time: {checkin.created}\n"

        # Retrieve the associated check-out object, if it exists
        checkout = Checkout.objects.filter(checkin=checkin).first()
        if checkout:
            report_content += f"Check-out Time: {checkout.created}\n"
        else:
            report_content += "Check-out Time: Not checked out\n"

        report_content += "\n"

    # Generate the response with the report content
    response = HttpResponse(report_content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="checkin_report.txt"'
    return response

def favicon_view(request):
    return HttpResponse("")