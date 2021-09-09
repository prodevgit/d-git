import click
import paramiko
from paramiko.ssh_exception import SSHException

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
def branch():
    dgit_instance.branch()

@main.command()
@click.argument('repository')
@click.option('--sshkey', '-sk')
def clone(sshkey,repository):
    print(sshkey)
    if '@' in repository:
        print('ssh')
        hostname,repository = repository.split(':')
        user,hostname = hostname.split('@')
        print(hostname)
        print(repository)
        from paramiko.client import SSHClient
        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(hostname=hostname,username=user,key_filename=sshkey)
            stdin, stdout, stderr = client.exec_command('/home/devd/dev/d-git-server/venv/bin/python /home/devd/dev/d-git-server/generate_ssh_token.py')
            # client.
            token = stdout.read().decode("utf8").strip()
            print(f'STDOUT: {token}')
            print(f'STDERR: {stderr.read().decode("utf8")}')
        except SSHException as e:
            print(e)
            print("Can't connect to Dgit SSH server. SSH Authentication failed")

        client.close()

        dgit_instance.clone(repository,'ssh',token)
    # dgit_instance.init_repo()
    # print("DGit initialized for your project")

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
    if branch:
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

if __name__ == "__main__":
    main()