# Generated by Django 3.2.8 on 2021-11-28 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_assignment_weightage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='marksgot',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
