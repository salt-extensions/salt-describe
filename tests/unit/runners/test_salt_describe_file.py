# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
import sys
from pathlib import PosixPath
from pathlib import WindowsPath
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest
import saltext.salt_describe.runners.salt_describe_file as salt_describe_file_runner
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_file_runner: {
            "__salt__": {"salt.execute": MagicMock()},
            "__opts__": {},
        },
    }


def test_file(tmp_path):
    testfile = tmp_path / "testfile"
    file_sls_contents = {
        str(testfile): {
            "file.managed": [
                {
                    "source": f"salt://minion/files/{testfile}",
                    "user": "testuser",
                    "group": "testgrp",
                    "mode": "0o664",
                },
            ],
        },
    }

    file_sls = yaml.dump(file_sls_contents)
    read_retval = {"minion": "contents of testfile"}
    stats_retval = {
        "minion": {
            "user": "testuser",
            "group": "testgrp",
            "mode": "0o664",
        },
    }
    execute_retvals = [read_retval, stats_retval]
    with patch.dict(
        salt_describe_file_runner.__salt__, {"salt.execute": MagicMock(side_effect=execute_retvals)}
    ):
        with patch.object(salt_describe_file_runner, "generate_files") as generate_mock:
            with patch.object(
                salt_describe_file_runner,
                "get_minion_state_file_root",
                return_value=tmp_path / "file_roots" / "minion",
            ) as get_minion_root_mock:
                with patch("salt.utils.files.fopen", mock_open()) as open_mock:
                    assert "Generated SLS file locations" in salt_describe_file_runner.file(
                        "minion", str(testfile)
                    )
                    generate_mock.assert_called_with(
                        {}, "minion", file_sls, sls_name="files", config_system="salt"
                    )
                    get_minion_root_mock.assert_called_with({}, "minion", config_system="salt")
                    open_mock().write.assert_called_with("contents of testfile")


def test_file_permission_denied(tmp_path, minion_opts, caplog):
    if sys.platform.startswith("win32"):
        perm_denied_error_log = (
            "Unable to create directory " "C:\\ProgramData\\Salt Project\\Salt\\srv\\salt\\minion"
        )
    else:
        perm_denied_error_log = "Unable to create directory /srv/salt/minion"

    testfile = tmp_path / "testfile"
    file_sls_contents = {
        str(testfile): {
            "file.managed": [
                {
                    "source": f"salt://minion/files/{testfile}",
                    "user": "testuser",
                    "group": "testgrp",
                    "mode": "0o664",
                },
            ],
        },
    }

    file_sls = yaml.dump(file_sls_contents)
    read_retval = {"minion": "contents of testfile"}
    stats_retval = {
        "minion": {
            "user": "testuser",
            "group": "testgrp",
            "mode": "0o664",
        },
    }
    execute_retvals = [read_retval, stats_retval]

    with patch.dict(
        salt_describe_file_runner.__salt__, {"salt.execute": MagicMock(side_effect=execute_retvals)}
    ):
        with patch.dict(salt_describe_file_runner.__opts__, minion_opts):
            with patch.object(PosixPath, "mkdir", side_effect=PermissionError), patch.object(
                WindowsPath, "mkdir", side_effect=PermissionError
            ):
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_file_runner.file("minion", str(testfile))
                    assert not ret
                    assert perm_denied_error_log in caplog.text
