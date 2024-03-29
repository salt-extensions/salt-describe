# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from pathlib import PosixPath
from pathlib import WindowsPath
from unittest.mock import call
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest
import saltext.salt_describe.modules.salt_describe_ssh_known_hosts as salt_describe_ssh_known_hosts_module
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_ssh_known_hosts_module: {
            "__salt__": {"config.get": MagicMock(return_value="minion")},
            "__opts__": {},
        },
    }


def test_ssh_virtual():
    ret = salt_describe_ssh_known_hosts_module.__virtual__()
    assert ret == "describe"


def test_ssh_user_keys():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
            "AAAAC": {
                "enc": "ssh-ed25519",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_known_hosts_sls_contents = {
        "AAA": {
            "ssh_auth.present": [
                {"user": "user"},
                {"enc": "ssh-rsa"},
            ]
        },
        "AAAAC": {
            "ssh_auth.present": [
                {"user": "user"},
                {"enc": "ssh-ed25519"},
            ]
        },
    }

    ssh_known_hosts_sls = yaml.dump(ssh_known_hosts_sls_contents)

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            ret = salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            )
            generate_mock.assert_called_with(
                {}, "minion", ssh_known_hosts_sls, sls_name="ssh_known_hosts", config_system="salt"
            )


def test_ssh_user_keys_comment():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": ['option1="value1"', 'option2="value2 flag2"'],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_known_hosts_sls_contents = {
        "AAA": {
            "ssh_auth.present": [
                {"user": "user"},
                {"enc": "ssh-rsa"},
                {"options": ['option1="value1"', 'option2="value2 flag2"']},
                {"comment": "/home/user/.ssh/id_rsa"},
            ]
        },
    }

    ssh_known_hosts_sls = yaml.dump(ssh_known_hosts_sls_contents)

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            ret = salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            )
            generate_mock.assert_called_with(
                {}, "minion", ssh_known_hosts_sls, sls_name="ssh_known_hosts", config_system="salt"
            )


def test_ssh_user_keys_options():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": ['option1="value1"', 'option2="value2 flag2"'],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_known_hosts_sls_contents = {
        "AAA": {
            "ssh_auth.present": [
                {"user": "user"},
                {"enc": "ssh-rsa"},
                {"options": ['option1="value1"', 'option2="value2 flag2"']},
                {"comment": "/home/user/.ssh/id_rsa"},
            ]
        },
    }

    ssh_known_hosts_sls = yaml.dump(ssh_known_hosts_sls_contents)

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            ret = salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            )
            generate_mock.assert_called_with(
                {}, "minion", ssh_known_hosts_sls, sls_name="ssh_known_hosts", config_system="salt"
            )


def test_ssh_known_hosts_permission_denied(caplog, minion_opts, perm_denied_error_log):
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
            "AAAAC": {
                "enc": "ssh-ed25519",
                "comment": "ed25519-key",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.dict(salt_describe_ssh_known_hosts_module.__opts__, minion_opts):
            with patch.object(PosixPath, "mkdir", side_effect=PermissionError), patch.object(
                WindowsPath, "mkdir", side_effect=PermissionError
            ):
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_ssh_known_hosts_module.ssh_known_hosts()
                    assert not ret
                    assert perm_denied_error_log in caplog.text


def test_ssh_known_hosts_parse_salt_ret_false(minion_opts):
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
            "AAAAC": {
                "enc": "ssh-ed25519",
                "comment": "ed25519-key",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    with patch.object(
        salt_describe_ssh_known_hosts_module, "parse_salt_ret"
    ) as parse_salt_ret_mock:
        parse_salt_ret_mock.return_value = False
        with patch.dict(
            salt_describe_ssh_known_hosts_module.__salt__,
            {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
        ):
            ret = salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            assert not ret


def test_ssh_user_keys():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
            "AAAAC": {
                "enc": "ssh-ed25519",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_known_hosts_sls_contents = {
        "AAA": {
            "ssh_auth.present": [
                {"user": "user"},
                {"enc": "ssh-rsa"},
            ]
        },
        "AAAAC": {
            "ssh_auth.present": [
                {"user": "user"},
                {"enc": "ssh-ed25519"},
            ]
        },
    }

    ssh_known_hosts_sls = yaml.dump(ssh_known_hosts_sls_contents)

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            ret = salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts()
            )
            generate_mock.assert_called_with(
                {}, "minion", ssh_known_hosts_sls, sls_name="ssh_known_hosts", config_system="salt"
            )


def test_ssh_user_keys_chef():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
            "AAAAC": {
                "enc": "ssh-ed25519",
                "options": [],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_known_hosts_rb_contents = """depends 'ssh_authorized_keys'
ssh_authorize_key 'user' do
  key 'AAA'
  user 'user'
end

ssh_authorize_key 'user' do
  key 'AAAAC'
  user 'user'
end
"""

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts(config_system="chef")
            )
            generate_mock.assert_called_with(
                {},
                "minion",
                ssh_known_hosts_rb_contents,
                sls_name="ssh_known_hosts",
                config_system="chef",
            )


def test_ssh_user_keys_options_chef():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": ["option1=value1", "option2=value2 flag2"],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_known_hosts_rb_contents = """depends 'ssh_authorized_keys'
ssh_authorize_key 'user' do
  key 'AAA'
  user 'user'
  options(
    'option1' => 'value1',
    'option2' => 'value2 flag2',
  )
end
"""

    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts(config_system="chef")
            )
            generate_mock.assert_called_with(
                {},
                "minion",
                ssh_known_hosts_rb_contents,
                sls_name="ssh_known_hosts",
                config_system="chef",
            )


def test_ssh_user_keys_ansible():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_auth_yml_contents = [
        {
            "name": "Manage SSH Auth Keys",
            "tasks": [
                {
                    "name": "Manage ssh-auth key AAA",
                    "ansible.posix.authorized_key": {
                        "key": "AAA",
                        "user": "user",
                    },
                },
            ],
            "hosts": "testgroup",
        }
    ]

    ssh_auth_yml = yaml.dump(ssh_auth_yml_contents)
    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts(
                    config_system="ansible", hosts="testgroup"
                )
            )
            generate_mock.assert_called_with(
                {},
                "minion",
                ssh_auth_yml,
                sls_name="ssh_known_hosts",
                config_system="ansible",
            )


def test_ssh_user_keys_options_ansible():
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": ["option1='value1'", "option2='value2 flag2'"],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_auth_yml_contents = [
        {
            "name": "Manage SSH Auth Keys",
            "tasks": [
                {
                    "name": "Manage ssh-auth key AAA",
                    "ansible.posix.authorized_key": {
                        "key": "AAA",
                        "user": "user",
                        "key_options": "option1='value1', option2='value2 flag2'",
                    },
                },
            ],
            "hosts": "testgroup",
        }
    ]

    ssh_auth_yml = yaml.dump(ssh_auth_yml_contents)
    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            assert (
                "Generated SLS file locations"
                in salt_describe_ssh_known_hosts_module.ssh_known_hosts(
                    config_system="ansible", hosts="testgroup"
                )
            )
            generate_mock.assert_called_with(
                {},
                "minion",
                ssh_auth_yml,
                sls_name="ssh_known_hosts",
                config_system="ansible",
            )


def test_ssh_user_keys_ansible_no_hosts(caplog):
    ssh_known_hosts = {
        "user": {
            "AAA": {
                "enc": "ssh-rsa",
                "comment": "/home/user/.ssh/id_rsa",
                "options": ["option1='value1'", "option2='value2 flag2'"],
                "fingerprint": "XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX:XX",
            },
        }
    }

    ssh_auth_yml_contents = [
        {
            "name": "Manage SSH Auth Keys",
            "tasks": [
                {
                    "name": "Manage ssh-auth key AAA",
                    "ansible.posix.authorized_key": {
                        "key": "AAA",
                        "user": "user",
                        "key_options": "option1='value1', option2='value2 flag2'",
                    },
                },
            ],
        }
    ]

    ssh_auth_yml = yaml.dump(ssh_auth_yml_contents)
    with patch.dict(
        salt_describe_ssh_known_hosts_module.__salt__,
        {"ssh.auth_keys": MagicMock(return_value=ssh_known_hosts)},
    ):
        with patch.object(salt_describe_ssh_known_hosts_module, "generate_files") as generate_mock:
            with caplog.at_level(logging.ERROR):
                assert (
                    "Generated SLS file locations"
                    in salt_describe_ssh_known_hosts_module.ssh_known_hosts(config_system="ansible")
                )
                generate_mock.assert_called_with(
                    {},
                    "minion",
                    ssh_auth_yml,
                    sls_name="ssh_known_hosts",
                    config_system="ansible",
                )

                assert "Hosts was not passed" in caplog.text
