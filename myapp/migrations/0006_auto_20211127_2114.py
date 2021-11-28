# Generated by Django 3.2.8 on 2021-11-27 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_auto_20211127_1615'),
    ]

    operations = [
        migrations.CreateModel(
            name='DirectMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_user', models.CharField(max_length=30)),
                ('fromuser', models.CharField(max_length=30)),
                ('what_mess', models.CharField(max_length=1000)),
            ],
        ),
        migrations.AddField(
            model_name='courses',
            name='creater_disable',
            field=models.CharField(default='F', max_length=1),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commentor_name', models.CharField(max_length=30)),
                ('comment_body', models.TextField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='myapp.courses')),
            ],
        ),
    ]