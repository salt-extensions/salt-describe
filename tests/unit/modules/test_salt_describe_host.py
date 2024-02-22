# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from pathlib import PosixPath
from pathlib import WindowsPath
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.salt_describe.modules.salt_describe_host as salt_describe_host_module
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_host_module: {
            "__salt__": {"config.get": MagicMock(return_value="minion")},
            "__opts__": {},
        },
    }


def test_host():
    """
    test describe.host
    """
    host_list = {
        "comment-0": ["# Host addresses"],
        "comment-1": ["# comment"],
        "127.0.0.1": {"aliases": ["localhost"]},
        "127.0.1.1": {"aliases": ["megan-precision5550"]},
        "::1": {"aliases": ["localhost", "ip6-localhost", "ip6-loopback"]},
        "ff02::1": {"aliases": ["ip6-allnodes"]},
        "ff02::2": {"aliases": ["ip6-allrouters"]},
    }

    host_sls_contents = {
        "host_file_content_0": {"host.present": [{"ip": "127.0.0.1"}, {"names": ["localhost"]}]},
        "host_file_content_1": {
            "host.present": [{"ip": "127.0.1.1"}, {"names": ["megan-precision5550"]}]
        },
        "host_file_content_2": {
            "host.present": [
                {"ip": "::1"},
                {"names": ["localhost", "ip6-localhost", "ip6-loopback"]},
            ]
        },
        "host_file_content_3": {"host.present": [{"ip": "ff02::1"}, {"names": ["ip6-allnodes"]}]},
        "host_file_content_4": {"host.present": [{"ip": "ff02::2"}, {"names": ["ip6-allrouters"]}]},
    }
    host_sls = yaml.dump(host_sls_contents)

    with patch.dict(
        salt_describe_host_module.__salt__, {"host.list_hosts": MagicMock(return_value=host_list)}
    ):
        with patch.object(salt_describe_host_module, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in salt_describe_host_module.host()
            generate_mock.assert_called_with(
                {}, "minion", host_sls, sls_name="host", config_system="salt"
            )


def test_host_permissioned_denied(minion_opts, caplog, perm_denied_error_log):
    """
    test describe.host
    """
    host_list = {
        "comment-0": ["# Host addresses"],
        "comment-1": ["# comment"],
        "127.0.0.1": {"aliases": ["localhost"]},
        "127.0.1.1": {"aliases": ["megan-precision5550"]},
        "::1": {"aliases": ["localhost", "ip6-localhost", "ip6-loopback"]},
        "ff02::1": {"aliases": ["ip6-allnodes"]},
        "ff02::2": {"aliases": ["ip6-allrouters"]},
    }

    with patch.dict(
        salt_describe_host_module.__salt__, {"host.list_hosts": MagicMock(return_value=host_list)}
    ):
        with patch.dict(salt_describe_host_module.__opts__, minion_opts):
            with patch.object(PosixPath, "mkdir", side_effect=PermissionError), patch.object(
                WindowsPath, "mkdir", side_effect=PermissionError
            ):
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_host_module.host()
                    assert not ret
                    assert perm_denied_error_log in caplog.text
