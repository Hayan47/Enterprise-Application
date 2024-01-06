from .models import File, FileLock, Group, Checkin, Checkout
from django_celery_beat.models import PeriodicTask, ClockedSchedule
from datetime import timedelta
from django.http import HttpResponse

class FileService:
    def __init__(self):
        self.user = None
    
    def set_user(self, user):
        self.user = user  

    def home(self):
        files = File.objects.all()
        return files
    
    def checkinFile(self, id):
        file = File.objects.get(id=id)
        if FileLock.objects.filter(file=file).exclude(user=self.user).exists():
            raise ValueError('File is checked in by another user')
        if file.group is not None:
            if not file.group.users.filter(id=self.user.id).exists():
                raise ValueError('No Access to file group')
        if not FileLock.objects.filter(file=file).exists():
            Checkin.objects.create(file=file, user=self.user)
            file.lock_file(self.user)
            lock = FileLock.objects.get(file=file, user=self.user)
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
        return file

    def checkoutFile(self, file):
        lock = FileLock.objects.get(file=file, user=self.user)
        PeriodicTask.objects.filter(name=f'files.tasks.automatic_check_out_{lock.id}', args=[lock.id]).delete()
        file.unlock_file(self.user)
        file.is_free = True 
        file.save()
        c = Checkin.objects.filter(file=file, user=self.user).order_by('-created').first()
        Checkout.objects.create(checkin=c)


    def bulkCheckin(self, ids):
        selected_files = File.objects.filter(id__in=ids)
        locked_files = FileLock.objects.filter(file_id__in=selected_files)
        if locked_files.exists():
        # for lock in locked_files:
        #     if not lock.user == request.user:
                locked_file_names = [lock.file.file.name for lock in locked_files]
                raise ValueError(f"The following files are locked: {', '.join(locked_file_names)}")
        else:
            print('1')
            for file in selected_files:
                file.lock_file(self.user)
                lock = FileLock.objects.get(file=file, user=self.user)
                file.is_free = False
                file.save()
                Checkin.objects.create(file=file, user=self.user)
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

    def check_file_status(self, id):
        file = File.objects.get(id=id)
        return file

    def downloadFile(self, id):
        file = File.objects.get(id=id)
        filename = file.file.name
        with open('media/{}'.format(filename), mode='rb') as f:
            file_contents = f.read()
        response = HttpResponse(file_contents, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'
        return response
    
    def generateReport(self, id):
        file = File.objects.get(id=id)
        checkins = Checkin.objects.filter(file=file)
        report_content = f"Check-in Report for File: {file}\n\n"
        for checkin in checkins:
            report_content += f"User: {checkin.user}\n"
            report_content += f"Check-in Time: {checkin.created}\n"
            checkout = Checkout.objects.filter(checkin=checkin).first()
            if checkout:
                report_content += f"Check-out Time: {checkout.created}\n"
            else:
                report_content += "Check-out Time: Not checked out\n"
            report_content += "\n"
        response = HttpResponse(report_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="checkin_report.txt"'
        return response
    


class GroupService:
    def __init__(self):
        self.user = None
    
    def set_user(self, user):
        self.user = user  

    def groupCheckin(self, id):
        group = Group.objects.get(id=id)
        if not self.user == group.owner:
            raise ValueError(f"No Access to group \"{group.name}\"")
        files = group.file_set.all()
        users = group.users.all()
        return group, files, users