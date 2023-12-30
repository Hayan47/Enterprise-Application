from celery import shared_task
from .models import FileLock, Checkout, Checkin

@shared_task
def automatic_check_out(lock_id):
    lock = FileLock.objects.get(id=lock_id)
    lock.file.is_free = True
    lock.file.save()
    lock.delete()
    c = Checkin.objects.filter(file=lock.file, user=lock.user).order_by('-created').first()
    Checkout.objects.create(checkin=c)
    print("File checked out automatically.")
    return "Done"
