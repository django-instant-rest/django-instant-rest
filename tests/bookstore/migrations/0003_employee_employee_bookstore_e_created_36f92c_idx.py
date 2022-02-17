# Generated by Django 4.0.2 on 2022-02-14 01:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0002_bookinventory_storelocation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.storelocation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='employee',
            index=models.Index(fields=['created_at'], name='bookstore_e_created_36f92c_idx'),
        ),
    ]