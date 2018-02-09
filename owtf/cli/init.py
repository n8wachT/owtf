import os

import click

from owtf.cli.base import cli


@cli.command(help='Create a default configuration')
@click.argument('path', default='~/.owtf/')
def init(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.makedirs(path)

    config_path = os.path.join(path, 'owtf.conf.py')
    if os.path.exists(config_path):
        click.confirm(
            'Configuration file already present at [{}]. Overwrite it?'.format(
                config_path),
            abort=True
        )

    click.echo('Configuration written at {}'.format(config_path))
