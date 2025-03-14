# Generated by Django 5.1.5 on 2025-02-17 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_allocation_adapter_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='allocation',
            name='adapter',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='asset_tag_number',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='bag',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='battery_sl',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='building',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='contact_number',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='department',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='emp_id',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='hard_disk',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='laptop_category',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='location',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='manager',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='manufacturer',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='model',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='mouse',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='other_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='allocation',
            name='others_category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='allocation',
            name='processor',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='project_specific',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='ram_size',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='request_number',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='seat_number',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='serial_number',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='allocation',
            name='short_term',
            field=models.CharField(default=None, max_length=50),
            preserve_default=False,
        ),
    ]
