"""
    RKD Snippet Cooperative
    =======================

    Autonomous RKD distribution dedicated for creating configuration sharing mechanisms
    (often called cooperatives, stores etc.)

"""

import os
from rkd.api.syntax import TaskDeclaration
from rkd import main as rkd_main
from rkd.standardlib.env import GetEnvTask
from rkd.standardlib.env import SetEnvTask
from rkd.standardlib.jinja import RenderDirectoryTask
from rkd.standardlib.jinja import FileRendererTask
from .tasks import CooperativeSnippetWizardTask
from .tasks import CooperativeSnippetInstallTask
from .tasks import CooperativeInstallTask
from .tasks import CooperativeSyncTask


def imports():
    return [
        TaskDeclaration(CooperativeSyncTask()),
        TaskDeclaration(CooperativeSnippetInstallTask()),
        TaskDeclaration(CooperativeInstallTask()),
        TaskDeclaration(CooperativeSnippetWizardTask()),
        TaskDeclaration(CooperativeSyncTask()),

        TaskDeclaration(GetEnvTask()),
        TaskDeclaration(SetEnvTask()),
        TaskDeclaration(FileRendererTask()),
        TaskDeclaration(RenderDirectoryTask())
    ]


def env_or_default(env_name: str, default: str):
    return os.environ[env_name] if env_name in os.environ else default


def main():
    os.environ['RKD_PATH'] = os.path.dirname(os.path.realpath(__file__)) + '/internal:' + os.getenv('RKD_PATH', '')
    os.environ['RKD_WHITELIST_GROUPS'] = env_or_default('RKD_WHITELIST_GROUPS', ':env,:cooperative')
    os.environ['RKD_ALIAS_GROUPS'] = env_or_default('RKD_ALIAS_GROUPS', '')
    os.environ['RKD_UI'] = env_or_default('RKD_UI', 'false')
    rkd_main()


if __name__ == '__main__':
    main()
