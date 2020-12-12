import os
from tempfile import TemporaryDirectory
from io import StringIO
from rkd.inputoutput import BufferedSystemIO
from rkd.inputoutput import IO
from rkd_cooperative import CooperativeSyncTask
from rkd_cooperative.test import BaseTestCase


class CooperativeSyncTaskTest(BaseTestCase):
    def test_functional_syncing_repository_is_cloning_then_doing_pull_next_time(self):
        """Functional test checking if there is a git clone and git pull performed"""

        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            io = BufferedSystemIO()
            r_io = IO()
            str_io = StringIO()

            task: CooperativeSyncTask = CooperativeSyncTask()
            self.satisfy_task_dependencies(task=task, io=io)

            args = {
                '--repositories': 'https://github.com/riotkit-org/riotkit-harbor-snippet-cooperative' +
                                       '@@791f617e664f3d0d50d485b88abe38b87cbb2525'
            }

            with r_io.capture_descriptors(enable_standard_out=True, stream=str_io):
                # first time, it should be `git clone`
                task.execute(self.mock_execution_context(task, args=args,
                                                         defined_args={'--repositories': {'default': ''}}))

                # second time it should be a `git checkout && git pull`
                task.execute(self.mock_execution_context(task, args=args,
                                                         defined_args={'--repositories': {'default': ''}}))

            content = str_io.getvalue()
            self.assertIn("Cloning into '.rkd/cooperative/riotkit-org/riotkit-harbor-snippet-cooperative'", content,
                          msg='Expected a git clone')
            self.assertIn("HEAD is now at 791f617 Modify structure", content,
                          msg='Expected checkout on branch')
            self.assertIn('791f617e664f3d0d50d485b88abe38b87cbb2525 -> FETCH_HEAD', content,
                          msg='Expected a pull on a commit')
            self.assertIn('Already up to date.', content,
                          msg='Expected a checkout')

    def test_extract_repository_name_from_git_url(self):
        tested_method = CooperativeSyncTask.extract_repository_name_from_git_url

        self.assertEqual('riotkit-org/riotkit-do', tested_method('https://github.com/riotkit-org/riotkit-do'))
        self.assertEqual('riotkit-org/riotkit-do', tested_method('https://github.com:5000/riotkit-org/riotkit-do'))
        self.assertEqual('riotkit-org/riotkit-do', tested_method('git@github.com:riotkit-org/riotkit-do.git'))
        self.assertEqual('riotkit-org/riotkit-do', tested_method('ssh://git@github.com:riotkit-org/riotkit-do.git'))
        self.assertEqual('riotkit-org/riotkit-do', tested_method('ssh://git@github.com:5000/riotkit-org/riotkit-do.git'))

    def test_functional_next_repository_will_be_cloned_even_if_first_fails(self):
        """Verify that repository "B" will be cloned even if "A" failed"""

        with TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)

            io = BufferedSystemIO()
            task: CooperativeSyncTask = CooperativeSyncTask()
            self.satisfy_task_dependencies(task=task, io=io)

            args = {
                '--repositories': 'https://github.com/riotkit-org/riotkit-harbor-snippet-cooperative' +
                                       '@@invalid-ref-name,' +
                                       'https://github.com/riotkit-org/empty'
            }

            result = task.execute(self.mock_execution_context(task, args=args))

            self.assertTrue(os.path.isdir('.rkd/cooperative/riotkit-org/empty'),
                            msg='Expected empty directory to be cloned for testing')
            self.assertIn('Failed to synchronize repository ' +
                          '"https://github.com/riotkit-org/riotkit-harbor-snippet-cooperative"', io.get_value())
            self.assertFalse(result)

    # todo: Cover case - cloning a local git repository from directory to directory
