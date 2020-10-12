# Generated by Django 2.2 on 2020-10-12 18:02

from django.db import migrations, models
import django.db.models.deletion
import django_mysql.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assembly',
            fields=[
                ('assembly_id', models.AutoField(primary_key=True, serialize=False)),
                ('accession', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, null=True)),
                ('long_name', models.CharField(max_length=255, null=True)),
                ('synonyms', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'assembly',
            },
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('data_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='genomics', max_length=45)),
            ],
            options={
                'db_table': 'data_type',
            },
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('file_type_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('settings', django_mysql.models.JSONField(default=dict)),
            ],
            options={
                'db_table': 'file_type',
            },
        ),
        migrations.CreateModel(
            name='Genome',
            fields=[
                ('genome_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
                ('trackdb_location', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'genome',
            },
        ),
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('hub_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('short_label', models.CharField(max_length=100)),
                ('long_label', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
                ('description_url', models.URLField()),
                ('email', models.EmailField(max_length=254)),
                ('data_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.DataType')),
            ],
            options={
                'db_table': 'hub',
            },
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taxon_id', models.IntegerField()),
                ('scientific_name', models.CharField(max_length=255, null=True)),
                ('common_name', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'species',
            },
        ),
        migrations.CreateModel(
            name='Visibility',
            fields=[
                ('visibility_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'visibility',
            },
        ),
        migrations.CreateModel(
            name='Trackdb',
            fields=[
                ('trackdb_id', models.AutoField(primary_key=True, serialize=False)),
                ('public', models.BooleanField(default=False)),
                ('description', models.TextField(null=True)),
                ('version', models.CharField(default='v1.0', max_length=10)),
                ('created', models.IntegerField(default=1602525770)),
                ('updated', models.IntegerField(null=True)),
                ('configurations', django_mysql.models.JSONField(default=dict)),
                ('status_message', models.CharField(max_length=45, null=True)),
                ('status_last_update', models.CharField(max_length=45, null=True)),
                ('source_url', models.CharField(max_length=255, null=True)),
                ('source_checksum', models.CharField(max_length=255, null=True)),
                ('assembly', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Assembly')),
                ('genome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Genome')),
                ('hub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Hub')),
            ],
            options={
                'db_table': 'trackdb',
            },
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('track_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=45)),
                ('short_label', models.CharField(max_length=45, null=True)),
                ('long_label', models.CharField(max_length=255, null=True)),
                ('big_data_url', models.CharField(max_length=255)),
                ('html', models.CharField(max_length=255, null=True)),
                ('meta', models.CharField(max_length=255, null=True)),
                ('additional_properties', django_mysql.models.JSONField(default=dict)),
                ('composite_parent', models.CharField(max_length=2, null=True)),
                ('file_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.FileType')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Track')),
                ('trackdb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Trackdb')),
                ('visibility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Visibility')),
            ],
            options={
                'db_table': 'track',
            },
        ),
        migrations.AddField(
            model_name='hub',
            name='species',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Species'),
        ),
        migrations.AddField(
            model_name='genome',
            name='hub',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Hub'),
        ),
        migrations.AddField(
            model_name='assembly',
            name='genome',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trackhubs.Genome'),
        ),
    ]
