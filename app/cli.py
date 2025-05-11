import click
from flask import current_app
from .secret import get_api_key


def register_cli(app):
    """Регистрирует команды для CLI."""

    # Команда для вывода текущего API-ключа
    @app.cli.command("show-api-key")
    def show_api_key():
        """Выводит текущий API-ключ."""

        click.echo(get_api_key())
