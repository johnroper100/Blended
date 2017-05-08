import os
import sys
import time

import click

from .app_functions import getVersion
from .build_functions import buildFiles
from .config_functions import createConfig, generateReqFolders
from .content_functions import createPage, createPost
from .ftp_functions import sendFTP
from .theme_functions import downloadTheme, setupTheme

# Very important, get the directory that the user wants to run commands in
cwd = os.getcwd()


@click.group()
@click.version_option(version=getVersion(), message='You are running Blended version %(version)s')
def cli():
    """Blended: Static Website Generator"""


@cli.command('init', short_help="Initate a new website")
def init():
    """Initiates a new website"""

    createConfig()
    generateReqFolders()


@cli.command('download-theme', short_help='Download a theme')
@click.argument('theme')
def download_theme(theme):
    """Download a theme from the Blended themes repository"""

    downloadTheme(theme)


@cli.command('setup-theme', short_help='Setup a theme')
@click.argument('theme')
def setup_theme(theme):
    """Setup a downloaded theme"""

    setupTheme(theme)


@cli.command('ftp', short_help='Upload the build files via ftp')
def send_ftp():
    """Upload the built website to FTP"""

    sendFTP()


@cli.command('create', short_help='Create content')
@click.argument('type')
def theme(type):
    """Create content for the website"""

    if type == "post":
        createPost()
    elif type == "page":
        createPage()
    else:
        print("The type you entered was not recognized!")


@cli.command('build', short_help="Build the website")
def build():
    """Builds the website"""

    reload(sys)
    sys.setdefaultencoding('utf8')

    buildFiles()


if __name__ == '__main__':
    cli()
