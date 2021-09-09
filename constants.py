OBJECT_PATH = '.dgit/objects'

INDEX_PATH = '.dgit/index'

BRANCH_PATH = '.dgit/branch'

HEAD = '.dgit/HEAD'

RECENT_PATH = './dgit/recent_registry'

BRANCH_REF = '.dgit/refs'


DGIT_IGNORE = '.dgitignore'

CLONE_BY_SSH = 'ssh'
CLONE_BY_USERAUTH = 'userauth'

DGIT_SSH_SERVER_COMMAND = '/home/devd/dev/d-git-server/venv/bin/python /home/devd/dev/d-git-server/generate_ssh_token.py'

class TColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    DIFF = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    WHITE = '\u001b[0m'
