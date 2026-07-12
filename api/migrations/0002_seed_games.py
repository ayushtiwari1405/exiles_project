from django.db import migrations

def seed_games(apps, schema_editor):
    Games = apps.get_model('api', 'Games')
    Games.objects.create(
        title="Tic-Tac-Toe",
        desc="A simple 2-player turn-based game. Align three of your marks to win!",
        url="http://localhost:3000/games/tictactoe"
    )
    Games.objects.create(
        title="Connect Four",
        desc="Drop checkers into the grid and try to get four in a row horizontally, vertically, or diagonally.",
        url="http://localhost:3000/games/connectfour"
    )
    Games.objects.create(
        title="Chess",
        desc="The classic board game of strategy and intelligence. Challenge a friend to a duel.",
        url="http://localhost:3000/games/chess"
    )

def remove_games(apps, schema_editor):
    Games = apps.get_model('api', 'Games')
    Games.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_games, remove_games),
    ]
