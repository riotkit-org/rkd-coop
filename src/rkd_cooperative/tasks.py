import os
import subprocess
from glob import glob
from argparse import ArgumentParser
from typing import Dict
from typing import Tuple
from urllib.parse import urlparse
from rkd.api.contract import ExecutionContext
from rkd.api.inputoutput import Wizard
from rkd.api.contract import TaskInterface
from rkd.api.contract import ArgumentEnv
from rkd.exception import MissingInputException
from .formatting import core_snippet_tasks_formatting

HARBOR_PATH = os.path.dirname(os.path.realpath(__file__)) + '/..'
REPOSITORIES_DIRECTORY = '.rkd/cooperative'


class BaseCooperativeTask(TaskInterface):
    def format_task_name(self, name) -> str:
        return core_snippet_tasks_formatting(name)

    def get_declared_envs(self) -> Dict[str, ArgumentEnv]:
        envs = super(BaseCooperativeTask, self).get_declared_envs()
        envs['COOP_REPOSITORIES'] = ArgumentEnv(name='COOP_REPOSITORIES', switch='--repositories', default='')

        return envs

    def get_group_name(self) -> str:
        return ':cooperative'

    def get_repositories_list(self, ctx: ExecutionContext) -> Dict[str, str]:
        try:
            repos = ctx.get_arg_or_env('--repositories').split(',')
            repos_with_branch = {}

            for repo in repos:
                parts = repo.split('@@')
                repos_with_branch[parts[0]] = parts[1] if len(parts) >= 2 else 'master'

            return repos_with_branch

        except MissingInputException:
            self.io().warn('No repositories specified')
            return {}


class CooperativeSyncTask(BaseCooperativeTask):
    """Synchronize repositories"""

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('--repositories', help='List of urls to repositories, comma separated')

    def get_name(self) -> str:
        return ':sync'

    def execute(self, ctx: ExecutionContext) -> bool:
        end_result = True

        for repository, branch in self.get_repositories_list(ctx).items():
            self.io().info('Syncing repository "%s"' % repository)

            if not self.sync_repository(repository, branch):
                self.io().error('Failed to synchronize repository "%s"' % repository)

                end_result = False
                continue

            self.io().info('Repository synced.')

        return end_result

    def sync_repository(self, git_url: str, branch: str):
        repository_dir = REPOSITORIES_DIRECTORY + '/' + self.extract_repository_name_from_git_url(git_url)

        try:
            if not os.path.isdir(repository_dir + '/'):
                self.sh(' '.join(['mkdir', '-p', repository_dir]))
                self.sh(' '.join(['git', 'clone', git_url, repository_dir]))
                self.sh('cd "%s" && git config advice.detachedHead false' % repository_dir)
                self.sh('cd "%s" && git checkout "%s"' % (repository_dir, branch))
                return True

            # pull the existing repository
            self.sh('''cd "%s" && git reset --hard HEAD && git checkout %s && git pull origin %s''' % (
                repository_dir, branch, branch
            ))

        except subprocess.CalledProcessError as e:
            self.io().error('Error fetching a git repository: %s' % str(e))
            return False

        return True

    @staticmethod
    def extract_repository_name_from_git_url(git_url: str) -> str:
        if git_url.startswith('http'):
            return urlparse(git_url).path[1:]

        if not git_url:
            return ''

        if os.path.isdir(git_url):
            return os.path.basename(git_url)

        separated = git_url[5:].split(':')

        if len(separated) < 2:
            raise Exception('Malformed GIT url "%s" in repositories list' % git_url)

        name = separated[1]
        parts = name.split('/')

        # support for custom GIT-SSH port (example: ssh://git@github.com:5000/riotkit-org/riotkit-do.git)
        if parts[0].isdecimal():
            name = '/'.join(parts[1:])

        if name.endswith('.git'):
            return name[0:-4]

        return name


class CooperativeInstallTask(BaseCooperativeTask):
    """Installs a snippet from the previously synchronized repository"""

    def get_name(self) -> str:
        return ':install'

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('name', help='Snippet name')

    def execute(self, ctx: ExecutionContext) -> bool:
        name = ctx.get_arg('name')

        category_name, pkg_name = self.extract_category_and_pkg_names(name)
        path = self.find_snippet_path(pkg_name, category_name)

        if not path:
            self.io().error('Snippet not found in any synchronized repository. ' +
                            'Did you forget to do :cooperative:sync?')
            return False

        self.io().info('Installing snippet from "%s"' % path)

        # mock rkd_path, so the snippet can override the tasks
        rkd_path = os.getenv('RKD_PATH', '')
        snippet_rkd_path = os.path.realpath('./' + path + '/.rkd')

        if snippet_rkd_path:
            os.putenv('RKD_PATH', (rkd_path + ':' + snippet_rkd_path).strip(':'))

        try:
            subprocess.check_call(['rkd', ':snippet:wizard', path])
            subprocess.check_call(['rkd', ':snippet:install', path])
        finally:
            if os.path.isfile('.rkd/tmp-wizard.json'):
                os.unlink('.rkd/tmp-wizard.json')

            os.putenv('RKD_PATH', rkd_path)

        return True

    def extract_category_and_pkg_names(self, name: str) -> Tuple[str, str]:
        parts = name.split('/')
        category_name = parts[0] if len(parts) >= 2 else ''
        pkg_name = '/'.join(parts[1:]) if len(parts) >= 2 else name

        self.io().debug('category_name=%s, pkg_name=%s' % (category_name, pkg_name))

        return category_name, pkg_name

    def find_snippet_path(self, name: str, category_name: str):
        """Finds a snippet path by name.

        Raises:
            Exception: When snippet exists in multiple repositories
        """

        found_path = None

        for snippet_path in self.list_snippets(category_name):
            snippet_name = os.path.basename(snippet_path)

            if snippet_name == name:
                if found_path is not None:
                    self.io().error(('Ambiguous match, %s exists in %s and in %s. ' +
                                    'Maybe try to prepend a category name if it is available?') %
                                    (name, found_path, snippet_path))
                    return ''

                found_path = snippet_path

        return found_path

    def list_snippets(self, category_name: str):
        inside_path = category_name + '/' if category_name else ''
        glob_path = '.rkd/cooperative/**/snippets/' + inside_path + '**/snippet.json'

        self.io().debug('glob_path=%s' % glob_path)
        dirs = glob(glob_path, recursive=True)

        return list(set(map(lambda name: os.path.dirname(name), dirs)))


class CooperativeSnippetWizardTask(BaseCooperativeTask):
    """Snippet wizard - to be overridden by custom task provided by snippet"""

    def get_group_name(self) -> str:
        return ':snippet'

    def get_name(self) -> str:
        return ':wizard'

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('path', help='Path to the root directory of the snippet files')

    def execute(self, ctx: ExecutionContext) -> bool:
        return True


class CooperativeSnippetInstallTask(BaseCooperativeTask):
    """Snippet installation - to be overridden by custom task provided by snippet"""

    def get_group_name(self) -> str:
        return ':snippet'

    def get_name(self) -> str:
        return ':install'

    def configure_argparse(self, parser: ArgumentParser):
        parser.add_argument('path', help='Path to the root directory of the snippet files')

    def execute(self, ctx: ExecutionContext) -> bool:
        wizard = Wizard(self)
        wizard.load_previously_stored_values()
        os.environ.update(wizard.answers)

        self.rkd([
            ':j2:directory-to-directory',
            '--source="%s"' % ctx.get_arg('path') + '/files/',
            '--target="./"',
            '--pattern="(.*)"',
            '--copy-not-matching-files',
            '--template-filenames'
        ])
        return True
