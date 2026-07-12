from django.db import migrations

def update_urls(apps, schema_editor):
    Games = apps.get_model('api', 'Games')
    try:
        tictactoe = Games.objects.get(title="Tic-Tac-Toe")
        tictactoe.url = "/games/tictactoe.html"
        tictactoe.save()
    except Games.DoesNotExist:
        pass

    try:
        connectfour = Games.objects.get(title="Connect Four")
        connectfour.url = "/games/connectfour.html"
        connectfour.save()
    except Games.DoesNotExist:
        pass

    try:
        chess = Games.objects.get(title="Chess")
        chess.url = "/games/chess.html"
        chess.save()
    except Games.DoesNotExist:
        pass

def rollback_urls(apps, schema_editor):
    Games = apps.get_model('api', 'Games')
    # Can set back to localhost:3000 if needed, but not strictly necessary for rollback
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_seed_games'),
    ]

    operations = [
        migrations.RunPython(update_urls, rollback_urls),
    ]
