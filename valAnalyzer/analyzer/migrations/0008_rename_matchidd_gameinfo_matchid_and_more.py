# Generated by Django 4.2 on 2023-04-14 06:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("analyzer", "0007_rename_matchid_gameinfo_matchidd_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="gameinfo",
            old_name="matchidd",
            new_name="matchid",
        ),
        migrations.RenameField(
            model_name="gameplayerinfo",
            old_name="matchidd",
            new_name="matchid",
        ),
        migrations.RenameField(
            model_name="gamerounds",
            old_name="matchidd",
            new_name="matchid",
        ),
        migrations.RenameField(
            model_name="gamestats",
            old_name="matchidd",
            new_name="matchid",
        ),
        migrations.RenameField(
            model_name="gametimeline",
            old_name="matchidd",
            new_name="matchid",
        ),
    ]