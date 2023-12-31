# Generated by Django 4.2.7 on 2023-12-01 10:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shortener', '0003_alter_shorturl_short_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShortUrlAccessLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip_address', models.CharField(max_length=1000)),
                ('user_agent', models.CharField(max_length=1000)),
                ('timestamp', models.DateTimeField()),
                ('short_url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shortener.shorturl')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
