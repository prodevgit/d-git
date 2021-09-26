import os
import sys
import click

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commands import DGitCommand

dgit_instance = DGitCommand()

@click.group()
def main():
    click.echo("This is a CLI built with Click ✨")
    if dgit_instance.active == False:
        exit()
@main.command()
def init():
    print(99999)
    dgit_instance.init_repo()
    print("DGit initialized for your project")

@main.command()
def branch():
    dgit_instance.branch()

@main.command()
@click.argument('repository')
@click.option('--sshkey', '-sk')
def clone(sshkey,repository):
    dgit_instance.clone(sshkey,repository)

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
@click.option('--branch', '-b')
@click.argument('parent', required=False)
# @click.option('--parent', '-p')
def checkout(branch,parent):
    print(branch)
    print(parent)
    if branch:
        print(branch)
        if parent:
            print("Creating a new branch under a parent")
            print(branch)
            print('Created branch')
            print(f'{parent}/{branch}')
        else:
            print('Creating a new branch')
            dgit_instance.checkout(branch)
    else:
        print('Creating a new branch')
        if parent:
            print('Created branch7')
            print(parent)
            dgit_instance.checkout(parent)
        else:
            print('Wrong arguments')

    # print('checkout',branch,name)
    # dgit_instance.checkout(branch)

@main.command()
@click.argument('path')
# @click.option('--init', '-i')
def add(path):
    dgit_instance.add(path)

@main.command()
# @click.option('--init', '-i')
def push():
    print('push')
    dgit_instance.push()

def entry():
    main()

if __name__ == "__main__":
    entry()
