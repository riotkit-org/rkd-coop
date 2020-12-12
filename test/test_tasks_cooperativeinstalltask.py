import os
import subprocess
from tempfile import TemporaryDirectory
from rkd.inputoutput import BufferedSystemIO
from rkd_cooperative import CooperativeInstallTask
from rkd_cooperative.test import BaseTestCase

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))


class CooperativeInstallTaskTest(BaseTestCase):
    def test_functional_is_installing_dummy_snippet(self):
        """Functional test for installing a snippet from offline repository - successful case"""

        with TemporaryDirectory() as tmp_dir:
            # prepare
            os.chdir(tmp_dir)
            subprocess.check_call(['cp', '-pr', TESTS_DIR + '/examples/.rkd', '.rkd'])
            subprocess.check_call(['mkdir', '-p', '.rkd/cooperative'])
            subprocess.check_call(['cp', '-pr', TESTS_DIR + '/examples/repository-1', '.rkd/cooperative/repository-1'])

            os.environ['__WIZARD_INPUT'] = 'iwa-ait.org'

            task: CooperativeInstallTask = CooperativeInstallTask()
            self.satisfy_task_dependencies(task=task, io=BufferedSystemIO())

            task.execute(self.mock_execution_context(task, args={'name': 'nginx'}))

            with open('nginx.conf', 'r') as test_rendered_config_file:
                content = test_rendered_config_file.read()

                self.assertIn('server_name  iwa-ait.org;', content)

    def test_functional_trying_to_install_non_existing_snippet(self):
        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)

            io = BufferedSystemIO()
            task: CooperativeInstallTask = CooperativeInstallTask()
            self.satisfy_task_dependencies(task=task, io=io)

            task.execute(self.mock_execution_context(task, args={'name': 'some-non-existing-snippet'}))
            self.assertIn('Snippet not found in any synchronized repository. Did you forget to do :cooperative:sync?',
                          io.get_value())

    def test_functional_ambiguous_match_will_be_reported_when_there_are_two_packages_of_same_name(self):
        """Test that when same package name is in multiple repositories, then no package would be installed
        and the error would be shown instead"""

        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            subprocess.check_call(['cp', '-pr', TESTS_DIR + '/examples/.rkd', '.rkd'])
            subprocess.check_call(['mkdir', '-p', '.rkd/cooperative'])
            subprocess.check_call(['cp', '-pr', TESTS_DIR + '/examples/repository-1', '.rkd/cooperative/repository-1'])

            # this copy will duplicate all snippets, that's the key of our test
            subprocess.check_call(['cp', '-pr', TESTS_DIR + '/examples/repository-1', '.rkd/cooperative/repository-copy'])

            io = BufferedSystemIO()
            task: CooperativeInstallTask = CooperativeInstallTask()
            self.satisfy_task_dependencies(task=task, io=io)

            task.execute(self.mock_execution_context(task, args={'name': 'nginx'}))
            self.assertIn('Ambiguous match, nginx exists in', io.get_value())
            self.assertIn('.rkd/cooperative/repository-1/snippets/nginx', io.get_value())
            self.assertIn('.rkd/cooperative/repository-copy/snippets/nginx', io.get_value())

    def test_extract_category_and_pkg_names_returns_package_name_and_category_name_when_those_are_given(self):
        task = CooperativeInstallTask()
        task._io = BufferedSystemIO()
        category_name, pkg_name = task.extract_category_and_pkg_names('harbor/redis')

        self.assertEqual('harbor', category_name)
        self.assertEqual('redis', pkg_name)

    def test_extract_category_and_pkg_names_returns_only_package_name_when_category_is_not_present(self):
        task = CooperativeInstallTask()
        task._io = BufferedSystemIO()
        category_name, pkg_name = task.extract_category_and_pkg_names('redis')

        self.assertEqual('', category_name)
        self.assertEqual('redis', pkg_name)

    def test_extract_category_and_pkg_names_returns_multiple_directories_in_pkg_name(self):
        task = CooperativeInstallTask()
        task._io = BufferedSystemIO()
        category_name, pkg_name = task.extract_category_and_pkg_names('harbor/db/kv/redis')

        self.assertEqual('harbor', category_name)
        self.assertEqual('db/kv/redis', pkg_name)
