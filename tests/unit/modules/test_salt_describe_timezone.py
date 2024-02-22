# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from pathlib import PosixPath
from pathlib import WindowsPath
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.salt_describe.modules.salt_describe_timezone as salt_describe_timezone_module
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_timezone_module: {
            "__salt__": {"config.get": MagicMock(return_value="minion")},
            "__opts__": {},
        },
    }


def test_timezone():
    """
    test describe.timezone
    """
    timezone_list = "America/Los_Angeles"

    timezone_sls_contents = {"America/Los_Angeles": {"timezone.system": []}}
    timezone_sls = yaml.dump(timezone_sls_contents)

    with patch.dict(
        salt_describe_timezone_module.__salt__,
        {"timezone.get_zone": MagicMock(return_value=timezone_list)},
    ):
        with patch.object(salt_describe_timezone_module, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in salt_describe_timezone_module.timezone()
            generate_mock.assert_called_with(
                {}, "minion", timezone_sls, sls_name="timezone", config_system="salt"
            )


def test_timezone_permission_denied(minion_opts, caplog, perm_denied_error_log):
    """
    test describe.timezone
    """
    timezone_list = "America/Los_Angeles"

    timezone_sls_contents = {"America/Los_Angeles": {"timezone.system": []}}
    timezone_sls = yaml.dump(timezone_sls_contents)

    with patch.dict(
        salt_describe_timezone_module.__salt__,
        {"timezone.get_zone": MagicMock(return_value=timezone_list)},
    ):
        with patch.dict(salt_describe_timezone_module.__opts__, minion_opts):
            with patch.object(PosixPath, "mkdir", side_effect=PermissionError), patch.object(
                WindowsPath, "mkdir", side_effect=PermissionError
            ):
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_timezone_module.timezone()
                    assert not ret
                    assert perm_denied_error_log in caplog.text
