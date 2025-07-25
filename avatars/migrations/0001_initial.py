# Generated by Django 4.2.11 on 2025-07-13 18:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import avatars.models
import avatars.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=avatars.models.get_shared_image_upload_path, validators=[avatars.validators.validate_image_file_extension, avatars.validators.validate_image_size])),
                ('caption', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_images', to=settings.AUTH_USER_MODEL)),
                ('shared_with', models.ManyToManyField(blank=True, related_name='received_images', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=avatars.models.get_avatar_upload_path, validators=[avatars.validators.validate_image_file_extension, avatars.validators.validate_image_size])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
