import click

from commands import DGitCommand

dgit_instance = DGitCommand()
@click.group()
def main():
    click.echo("This is a CLI built with Click ✨")

@main.command()
# @click.argument('name')
# @click.option('--init', '-i')
def init():
    dgit_instance.init_repo()
    print("DGit initialized for your project")

@main.command()
def status():
    dgit_instance.status()

@main.command()
def diff():
    dgit_instance.diff()

@main.command()
# @click.argument('name')
# @click.option('--init', '-i')
def stash():
    dgit_instance.stash()


@main.command()
@click.argument('path')
# @click.option('--init', '-i')
def add(path):
    print(path)

if __name__ == "__main__":
    main()