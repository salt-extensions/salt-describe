# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=line-too-long
import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import yaml

import saltext.salt_describe.runners.salt_describe_beacon as salt_describe_beacon_runner

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_beacon_runner: {
            "__salt__": {"salt.execute": MagicMock()},
            "__opts__": {},
        },
    }


@pytest.fixture
def beacon_ret():
    yield {
        "minion": {
            "watch_important_file": [
                {"files": {"/etc/important_file": {"mask": ["modify"]}}},
                {"beacon_module": "inotify"},
            ],
            "watch_another_file": [
                {"files": {"/etc/another_file": {"mask": ["modify"]}}},
                {"beacon_module": "inotify"},
            ],
            "load": [
                {"averages": {"1m": [0.0, 2.0], "5m": [0.0, 1.5], "15m": [0.1, 1.0]}},
                {"interval": 10},
            ],
        }
    }


def test_beacon(tmp_path, beacon_ret):
    expected_sls = {
        "watch_important_file": {
            "beacon.present": [
                {"files": {"/etc/important_file": {"mask": ["modify"]}}},
                {"beacon_module": "inotify"},
            ]
        },
        "watch_another_file": {
            "beacon.present": [
                {"files": {"/etc/another_file": {"mask": ["modify"]}}},
                {"beacon_module": "inotify"},
            ]
        },
        "load": {
            "beacon.present": [
                {"averages": {"1m": [0.0, 2.0], "5m": [0.0, 1.5], "15m": [0.1, 1.0]}},
                {"interval": 10},
            ]
        },
    }

    beacon_sls = yaml.dump(expected_sls)

    with patch.dict(
        salt_describe_beacon_runner.__salt__, {"salt.execute": MagicMock(return_value=beacon_ret)}
    ):
        with patch.object(salt_describe_beacon_runner, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in salt_describe_beacon_runner.beacon("minion")
            generate_mock.assert_called_with(
                {}, "minion", beacon_sls, sls_name="beacon", config_system="salt"
            )
