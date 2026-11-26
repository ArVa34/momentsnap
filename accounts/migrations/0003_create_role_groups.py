from django.db import migrations

# The group names are written out here on purpose: a migration is a snapshot in history,
# so it must not depend on application code that may change later.
ROLE_GROUPS = ["Administrators", "Event hosts"]


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ROLE_GROUPS:
        Group.objects.get_or_create(name=name)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=ROLE_GROUPS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_city_user_phone_alter_user_email"),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]