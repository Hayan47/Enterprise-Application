from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.contrib import messages

def delete_user_with_filelock_check(self):
    if FileLock.objects.filter(user=self).exists():
        # Don't allow delete
        
        raise ValidationError('Cannot delete user with active file locks')
    super(User, self).delete()

User.delete = delete_user_with_filelock_check


class Group(Group):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    created = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.name

class File(models.Model):
    file = models.FileField(upload_to='uploads/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_free = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.file.name

    class Meta:
        ordering = ['-created']  

    def delete(self):
        self.file.delete()
        super().delete()


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     files = models.ManyToManyField(File)
#     groups = models.ManyToManyField(Group)


class FileLock(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    locked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.file.name + ' by ' + self.user.username
    

class Checkin(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='checkins')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Check-ins'

    def __str__(self):
        return f'Checkin {self.pk} for {self.file.file.name}'


class Checkout(models.Model):
    checkin = models.OneToOneField(Checkin, on_delete=models.CASCADE, related_name='checkout')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Check-outs'

    def __str__(self):
        return f'Checkout {self.pk} for {self.checkin}'