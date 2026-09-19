from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("world", "0003_enemy"),
    ]

    operations = [
        migrations.AddField(
            model_name="adventure",
            name="generated_scenario",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
