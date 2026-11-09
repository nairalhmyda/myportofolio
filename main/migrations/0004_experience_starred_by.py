from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0003_project_project_image_url_project_starred_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="experience",
            name="starred_by",
            field=models.ManyToManyField(
                blank=True,
                related_name="starred_experiences",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
