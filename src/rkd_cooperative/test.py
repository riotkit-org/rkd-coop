import os
import unittest
from copy import deepcopy
from abc import ABC


class BaseTestCase(unittest.TestCase, ABC):
    _original_cwd: str
    _original_environ: dict

    def setUp(self) -> None:
        self._original_cwd = os.getcwd()
        self._original_environ = deepcopy(os.environ)

    def tearDown(self) -> None:
        os.chdir(self._original_cwd)
        os.environ = self._original_environ
