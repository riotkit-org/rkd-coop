
from rkd.syntax import TaskAliasDeclaration as Task
from harbor import imports as HarborImports
from rkd_python import imports as PythonImports

IMPORTS = [] + PythonImports() + HarborImports()

TASKS = [
    Task(':release', description='Release to PyPI (snapshot when on master, release on tag)',
         to_execute=[
            ':py:build', ':py:publish', '--username=__token__', '--password=${PYPI_TOKEN}'
         ]),

    Task(':test', [':py:unittest'], description='Run unit tests'),
]
