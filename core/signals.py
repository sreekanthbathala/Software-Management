from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, Notification, ActivityLog

@receiver(pre_save, sender=Task)
def capture_old_task_state(sender, instance, **kwargs):
    if instance.id:
        instance._old_state = Task.objects.get(id=instance.id)
    else:
        instance._old_state = None

@receiver(post_save, sender=Task)
def log_task_changes(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            task=instance,
            action=f"Task created and assigned to {instance.assigned_to.username if instance.assigned_to else 'nobody'}."
        )
    elif hasattr(instance, '_old_state') and instance._old_state:
        old = instance._old_state
        if old.status != instance.status:
            ActivityLog.objects.create(
                task=instance,
                action=f"Status changed from '{old.status}' to '{instance.status}'."
            )
        if old.priority != instance.priority:
            ActivityLog.objects.create(
                task=instance,
                action=f"Priority changed from '{old.priority}' to '{instance.priority}'."
            )

@receiver(post_save, sender=Task)
def notify_task_assignment(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to,
            message=f"You have been assigned a new task: '{instance.title}'."
        )
        if instance.assigned_to.email:
            message_text = f"Hello {instance.assigned_to.username},\n\nYou have been assigned a new task: '{instance.title}'.\nDue Date: {instance.due_date}\nPriority: {instance.priority}"
            send_mail(
                subject='New Task Assigned - SoftManage',
                message=message_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.assigned_to.email],
                fail_silently=True,
            )