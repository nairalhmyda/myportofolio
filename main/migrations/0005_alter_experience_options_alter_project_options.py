from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0004_experience_starred_by"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="experience",
            options={"ordering": ["-started_at"]},
        ),
        migrations.AlterModelOptions(
            name="project",
            options={"ordering": ["-year", "title"]},
        ),
    ]
