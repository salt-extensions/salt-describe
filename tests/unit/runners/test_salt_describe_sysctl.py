# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from pathlib import PosixPath
from pathlib import WindowsPath
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import yaml

import saltext.salt_describe.runners.salt_describe_sysctl as salt_describe_sysctl_runner

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_sysctl_runner: {
            "__salt__": {"salt.execute": MagicMock()},
            "__opts__": {},
        },
    }


def test_sysctl():
    sysctl_show = {"minion": {"vm.swappiness": 60, "vm.vfs_cache_pressure": 100}}

    sysctl_sls_contents = {
        "sysctl-vm.swappiness": {
            "sysctl.present": [
                {"name": "vm.swappiness"},
                {"value": 60},
            ],
        },
    }
    sysctl_sls = yaml.dump(sysctl_sls_contents)

    with patch.dict(
        salt_describe_sysctl_runner.__salt__, {"salt.execute": MagicMock(return_value=sysctl_show)}
    ):
        with patch.object(salt_describe_sysctl_runner, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in salt_describe_sysctl_runner.sysctl(
                "minion", ["vm.swappiness"]
            )
            generate_mock.assert_called_with(
                {}, "minion", sysctl_sls, sls_name="sysctl", config_system="salt"
            )


def test_sysctl_permission_denied(caplog, minion_opts, perm_denied_error_log):
    sysctl_show = {"minion": {"vm.swappiness": 60, "vm.vfs_cache_pressure": 100}}

    with patch.dict(
        salt_describe_sysctl_runner.__salt__, {"salt.execute": MagicMock(return_value=sysctl_show)}
    ):
        with patch.dict(salt_describe_sysctl_runner.__opts__, minion_opts):
            with (
                patch.object(PosixPath, "mkdir", side_effect=PermissionError),
                patch.object(WindowsPath, "mkdir", side_effect=PermissionError),
            ):
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_sysctl_runner.sysctl("minion", ["vm.swappiness"])
                    assert not ret
                    assert perm_denied_error_log in caplog.text


def test_sysctl_configuration_file(master_opts):
    sysctl_show = {
        "minion": {"vm.swappiness": 60, "vm.laptop_mode": 0, "vm.vfs_cache_pressure": 100}
    }

    sysctl_sls_contents = {
        "sysctl-vm.swappiness": {
            "sysctl.present": [
                {"name": "vm.swappiness"},
                {"value": 60},
            ],
        },
        "sysctl-vm.laptop_mode": {
            "sysctl.present": [
                {"name": "vm.laptop_mode"},
                {"value": 0},
            ],
        },
    }
    sysctl_sls = yaml.dump(sysctl_sls_contents)

    master_opts["describe"] = {
        "minion": {
            "sysctl": {"sysctl_items": ["vm.swappiness", "vm.laptop_mode"]},
        }
    }

    salt_execute_mock = MagicMock(return_value=sysctl_show)

    with patch.dict(salt_describe_sysctl_runner.__opts__, master_opts):
        with patch.dict(salt_describe_sysctl_runner.__salt__, {"salt.execute": salt_execute_mock}):
            with patch.object(salt_describe_sysctl_runner, "generate_files") as generate_mock:
                ret = salt_describe_sysctl_runner.sysctl("minion")
                assert "Generated SLS file locations" in ret
                generate_mock.assert_called_with(
                    master_opts, "minion", sysctl_sls, sls_name="sysctl", config_system="salt"
                )
