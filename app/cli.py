import click
from flask import current_app
from .secret import get_api_key

def register_cli(app):
    @app.cli.command("show-api-key")
    def show_api_key():
        """Выводит текущий API-ключ для админских операций."""
        click.echo(get_api_key())
