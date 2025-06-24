# Generated manually to clean up removed models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0005_add_color_to_skill'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS resumes_skilltagrelation;",
            reverse_sql="",
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS resumes_skilltag;",
            reverse_sql="",
        ),
    ]