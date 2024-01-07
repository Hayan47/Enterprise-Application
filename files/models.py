from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.conf import settings

MAX_UPLOAD_FILES = settings.MAX_UPLOAD_FILES

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

    def lock_file(self, user):
        FileLock.objects.create(file=self, user=user)

    def unlock_file(self, user):
        FileLock.objects.filter(file=self, user=user).delete()
    
    def save(self, *args, **kwargs):
        # Count the number of files the user has already uploaded
        user_file_count = File.objects.filter(owner=self.owner).count()

        # Check if the count exceeds the maximum allowed
        if user_file_count >= MAX_UPLOAD_FILES:
            raise ValidationError(f"Cannot upload more than {MAX_UPLOAD_FILES} files.")
        
        super(File, self).save(*args, **kwargs)

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