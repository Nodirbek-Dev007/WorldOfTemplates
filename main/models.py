from django.db import models
from django.contrib.auth.models import User
import os
import uuid
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, unique=True, blank=True)
    image = models.ImageField(default='profile/profile_pic.png', upload_to='profile/', null=True, blank=True)

    def __str__(self):
        return self.username if self.username else "Unnamed Customer"

class Tag(models.Model):
    tag_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag_name

class Product(models.Model):
    CATEGORIES = [
        'Office 2013', 'Office 2016', 'Office 2019', 'Office 2021', 'Office 2024', 'Office 365',
    ]
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )

    product_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads')
    office_created = models.CharField(max_length=200, choices=[(cat, cat) for cat in CATEGORIES], null=True, blank=True)
    morph = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)
    favorite = models.BooleanField(default=False)
    product_type = models.ManyToManyField(Tag, blank=True)
    size = models.FloatField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(null=True, blank=True)
    slide_images = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.product_name if self.product_name else "Unnamed Product"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        uploaded_file = None
        if self.file and is_new:
            uploaded_file = self.file
            self.file = None
        super().save(*args, **kwargs)

        if is_new and uploaded_file:
            try:
                unique_id = str(uuid.uuid4())
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', unique_id)
                os.makedirs(upload_dir, exist_ok=True)
                pptx_path = os.path.join(upload_dir, uploaded_file.name)

                with open(pptx_path, 'wb+') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                self.size = uploaded_file.size / (1024 * 1024)

                if not pptx_path.lower().endswith(('.pptx', '.pptm', '.ppt')):
                    self.status = 'processed'
                    self.file.name = f'uploads/{unique_id}/{uploaded_file.name}'
                    super().save(update_fields=['file', 'status', 'size'])
                    return

                self.file.name = f'uploads/{unique_id}/{uploaded_file.name}'
                super().save(update_fields=['file', 'size'])

                from .tasks import process_pptx_slides
                process_pptx_slides(self.id, pptx_path, unique_id)

            except Exception as e:
                error_message = f"Error saving product file {uploaded_file.name}: {str(e)}"
                logger.error(error_message)
                self.status = 'failed'
                self.error_message = error_message
                super().save(update_fields=['status', 'error_message'])