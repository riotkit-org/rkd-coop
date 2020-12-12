import os
from copy import deepcopy
from abc import ABC
from rkd.api.testing import BasicTestingCase


class BaseTestCase(BasicTestingCase, ABC):
    _original_cwd: str
    _original_environ: dict

    def setUp(self) -> None:
        self._original_cwd = os.getcwd()
        self._original_environ = deepcopy(os.environ)

    def tearDown(self) -> None:
        os.chdir(self._original_cwd)
        os.environ = self._original_environ
