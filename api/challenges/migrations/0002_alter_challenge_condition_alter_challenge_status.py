# Generated by Django 5.1.3 on 2025-01-06 00:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("challenges", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="challenge",
            name="condition",
            field=models.CharField(
                choices=[
                    ("github_commits", "GITHUB_COMMITS"),
                    ("problem_solving", "PROBLEM_SOLVING"),
                ],
                max_length=20,
                verbose_name="Competition Condition",
            ),
        ),
        migrations.AlterField(
            model_name="challenge",
            name="status",
            field=models.CharField(
                choices=[
                    ("ongoing", "ONGOING"),
                    ("completed", "COMPLETED"),
                    ("rejected", "REJECTED"),
                ],
                default="ongoing",
                max_length=20,
                verbose_name="Status",
            ),
        ),
    ]
