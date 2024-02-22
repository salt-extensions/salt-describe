# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import os
import sys

import pytest
import salt.config
from saltext.salt_describe import PACKAGE_ROOT
from saltfactories.utils import random_string


@pytest.fixture(scope="session")
def salt_factories_config():
    """
    Return a dictionary with the keyworkd arguments for FactoriesManager
    """
    return {
        "code_dir": str(PACKAGE_ROOT),
        "start_timeout": 120 if os.environ.get("CI") else 60,
    }


@pytest.fixture(scope="package")
def master(salt_factories, base_env_state_tree_root_dir):
    config_defaults = {
        "file_roots": {
            "base": [
                str(base_env_state_tree_root_dir),
            ]
        },
        "enable_fqdns_grains": False,
        "timeout": 120,
    }

    return salt_factories.salt_master_daemon(random_string("master-"), defaults=config_defaults)


@pytest.fixture(scope="package")
def minion(master):
    config_defaults = {"enable_fqdns_grains": False, "timeout": 120}
    return master.salt_minion_daemon(random_string("minion-"), defaults=config_defaults)


@pytest.fixture(scope="session")
def integration_files_dir(salt_factories):
    """
    Fixture which returns the salt integration files directory path.
    Creates the directory if it does not yet exist.
    """
    dirname = salt_factories.root_dir / "integration-files"
    dirname.mkdir(exist_ok=True)
    return dirname


@pytest.fixture(scope="session")
def state_tree_root_dir(integration_files_dir):
    """
    Fixture which returns the salt state tree root directory path.
    Creates the directory if it does not yet exist.
    """
    dirname = integration_files_dir / "state-tree"
    dirname.mkdir(exist_ok=True)
    return dirname


@pytest.fixture(scope="session")
def base_env_state_tree_root_dir(state_tree_root_dir):
    """
    Fixture which returns the salt base environment state tree directory path.
    Creates the directory if it does not yet exist.
    """
    dirname = state_tree_root_dir / "base"
    dirname.mkdir(exist_ok=True)
    return dirname


@pytest.fixture
def minion_opts(tmp_path):
    """
    Default minion configuration with relative temporary paths to not require root permissions.
    """
    root_dir = tmp_path / "minion"
    opts = salt.config.DEFAULT_MINION_OPTS.copy()
    opts["__role"] = "minion"
    opts["root_dir"] = str(root_dir)
    for name in ("cachedir", "pki_dir", "sock_dir", "conf_dir"):
        dirpath = root_dir / name
        dirpath.mkdir(parents=True)
        opts[name] = str(dirpath)
    opts["log_file"] = "logs/minion.log"
    return opts


@pytest.fixture
def master_opts(tmp_path):
    """
    Default master configuration with relative temporary paths to not require root permissions.
    """
    root_dir = tmp_path / "master"
    opts = salt.config.DEFAULT_MASTER_OPTS.copy()
    opts["__role"] = "master"
    opts["root_dir"] = str(root_dir)
    for name in ("cachedir", "pki_dir", "sock_dir", "conf_dir"):
        dirpath = root_dir / name
        dirpath.mkdir(parents=True)
        opts[name] = str(dirpath)
    opts["log_file"] = "logs/master.log"
    return opts


@pytest.fixture
def perm_denied_error_log():
    if sys.platform.startswith("win32"):
        perm_denied_error_log = (
            "Unable to create directory "
            "C:\\ProgramData\\Salt Project\\Salt\\srv\\salt\\minion.  "
            "Check that the salt user has the correct permissions."
        )
    else:
        perm_denied_error_log = (
            "Unable to create directory /srv/salt/minion.  "
            "Check that the salt user has the correct permissions."
        )
    return perm_denied_error_log
