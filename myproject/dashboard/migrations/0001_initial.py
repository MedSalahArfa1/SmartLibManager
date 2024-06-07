# Generated by Django 4.2.9 on 2024-05-29 14:07

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('central_id', models.CharField(max_length=10)),
                ('local_id', models.CharField(max_length=10)),
                ('title', models.CharField(max_length=100)),
                ('quantity_available', models.PositiveIntegerField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('user_cin', models.CharField(max_length=8)),
                ('authors', models.ManyToManyField(to='dashboard.author')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('zipCode', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('birth_date', models.DateField()),
                ('cin', models.CharField(blank=True, max_length=8, null=True)),
                ('address', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('membership_id', models.CharField(max_length=10)),
                ('membership_validity', models.DateField(default=datetime.date(2025, 5, 29))),
                ('user_cin', models.CharField(max_length=8)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.library')),
            ],
            options={
                'unique_together': {('membership_id', 'library'), ('cin', 'library'), ('email', 'library')},
            },
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_date', models.DateField(auto_now_add=True)),
                ('visit_time', models.TimeField(auto_now_add=True)),
                ('user_cin', models.CharField(max_length=8)),
                ('book', models.ManyToManyField(to='dashboard.book')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.library')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.user')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('transaction_type', models.CharField(choices=[('get', 'Get'), ('return', 'Return')], max_length=10)),
                ('return_date', models.DateField(blank=True, null=True)),
                ('user_cin', models.CharField(max_length=8)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.book')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.library')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.user')),
            ],
            options={
                'ordering': ['-transaction_date'],
            },
        ),
        migrations.AddField(
            model_name='book',
            name='categories',
            field=models.ManyToManyField(to='dashboard.category'),
        ),
        migrations.AddField(
            model_name='book',
            name='library',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.library'),
        ),
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('birth_date', models.DateField()),
                ('cin', models.CharField(max_length=8, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=100)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_authenticated', models.BooleanField(default=True)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.library')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='book',
            unique_together={('central_id', 'library'), ('local_id', 'library')},
        ),
    ]