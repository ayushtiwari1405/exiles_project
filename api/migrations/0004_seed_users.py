import sys
from django.db import migrations, connection
from django.contrib.auth.hashers import make_password

def seed_users(apps, schema_editor):
    db_name = connection.settings_dict.get('NAME')
    db_name_str = str(db_name) if db_name is not None else ''
    if 'test' in sys.argv or db_name_str.startswith('test_') or db_name_str == ':memory:':
        return

    User = apps.get_model('api', 'User')
    hashed_pw = make_password('password123')
    
    for username in ['alice', 'bob', 'jack']:
        if not User.objects.filter(username=username).exists():
            User.objects.create(username=username, password_hash=hashed_pw)

def remove_users(apps, schema_editor):
    User = apps.get_model('api', 'User')
    User.objects.filter(username__in=['alice', 'bob', 'jack']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_update_game_urls'),
    ]

    operations = [
        migrations.RunPython(seed_users, remove_users),
    ]
