# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from pathlib import PosixPath
from pathlib import WindowsPath
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.salt_describe.modules.salt_describe_pip as salt_describe_pip_module
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_pip_module: {
            "__salt__": {"config.get": MagicMock(return_value="minion")},
            "__opts__": {},
        },
    }


def test_pip():
    pip_list = [
        "requests==0.1.2",
        "salt==3004.1",
        "argcomplete==2.3.4-5",
    ]

    expected_sls_write = yaml.dump(
        {
            "installed_pip_libraries": {"pip.installed": [{"pkgs": pip_list}]},
        }
    )
    with patch.dict(
        salt_describe_pip_module.__salt__, {"pip.freeze": MagicMock(return_value=pip_list)}
    ):
        with patch.object(salt_describe_pip_module, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in salt_describe_pip_module.pip()
            generate_mock.assert_called_with(
                {}, "minion", expected_sls_write, sls_name="pip", config_system="salt"
            )


def test_pip_ansible():
    hosts = "testgroup"
    pip_list = [
        "requests==0.1.2",
        "salt==3004.1",
        "argcomplete==2.3.4-5",
    ]

    expected_yml_write = yaml.dump(
        [
            {
                "tasks": [
                    {
                        "name": "installed_pip_libraries",
                        "ansible.builtin.pip": {
                            "name": ["requests==0.1.2", "salt==3004.1", "argcomplete==2.3.4-5"]
                        },
                    }
                ],
                "hosts": "testgroup",
            }
        ]
    )
    with patch.dict(
        salt_describe_pip_module.__salt__, {"pip.freeze": MagicMock(return_value=pip_list)}
    ):
        with patch.object(salt_describe_pip_module, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in (
                salt_describe_pip_module.pip(config_system="ansible", hosts=hosts)
            )
            generate_mock.assert_called_with(
                {},
                "minion",
                expected_yml_write,
                sls_name="pip",
                config_system="ansible",
            )


def test_pip_permission_denied(minion_opts, caplog, perm_denied_error_log):
    pip_list = [
        "requests==0.1.2",
        "salt==3004.1",
        "argcomplete==2.3.4-5",
    ]

    with patch.dict(
        salt_describe_pip_module.__salt__, {"pip.freeze": MagicMock(return_value=pip_list)}
    ):
        with patch.dict(salt_describe_pip_module.__opts__, minion_opts):
            with patch.object(PosixPath, "mkdir", side_effect=PermissionError), patch.object(
                WindowsPath, "mkdir", side_effect=PermissionError
            ):
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_pip_module.pip()
                    assert not ret
                    assert perm_denied_error_log in caplog.text
