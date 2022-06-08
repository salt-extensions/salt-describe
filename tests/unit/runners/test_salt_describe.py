import pytest

from unittest.mock import patch, MagicMock, mock_open, call

import saltext.salt_describe.runners.salt_describe as salt_describe_runner

import salt.config
import salt.runners.salt as salt_runner

import yaml

import logging

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    module_globals = {
        "__salt__": {"salt.execute": salt_runner.execute},
        "__opts__": salt.config.DEFAULT_MASTER_OPTS.copy(),
    }
    return {
        salt_describe_runner: module_globals,
    }


def test_pkg():
    pkg_list = {
        "minion": {
            "pkg1": "0.1.2-3",
            "pkg2": "1.2rc5-3",
            "pkg3": "2.3.4-5",
            "pk4": "3.4-5",
            "pkg5": "4.5.6-7",
        }
    }

    expected_calls = [
        call().write(
            "installed_packages:\n  pkg.installed:\n  - pkgs:\n    - pkg1: 0.1.2-3\n    - pkg2: 1.2rc5-3\n    - pkg3: 2.3.4-5\n    - pk4: 3.4-5\n    - pkg5: 4.5.6-7\n"
        ),
        call().write("include:\n- minion.pkgs\n"),
    ]
    with patch.dict(
        salt_describe_runner.__salt__, {"salt.execute": MagicMock(return_value=pkg_list)}
    ):
        with patch.dict(
            salt_describe_runner.__salt__,
            {"config.get": MagicMock(return_value=["/srv/salt", "/srv/spm/salt"])},
        ):
            with patch("os.listdir", return_value=["pkgs.sls"]):
                with patch("salt.utils.files.fopen", mock_open()) as open_mock:
                    assert salt_describe_runner.pkg("minion") == True
                    open_mock.assert_has_calls(expected_calls, any_order=True)


def test_host(tmp_path):
    """
    test describe.host
    """
    host_list = {'poc-minion': {'comment-0': ['# Host addresses'],
                                'comment-1': ['# comment'],
                                '127.0.0.1': {'aliases': ['localhost']},
                                '127.0.1.1': {'aliases': ['megan-precision5550']},
                                '::1': {'aliases': ['localhost', 'ip6-localhost', 'ip6-loopback']},
                                'ff02::1': {'aliases': ['ip6-allnodes']},
                                'ff02::2': {'aliases': ['ip6-allrouters']}}}

    expected_content = {'host_file_content_0': {'host.present': [{'ip': '127.0.0.1'}, {'names': ['localhost']}]},
                        'host_file_content_1': {'host.present': [{'ip': '127.0.1.1'}, {'names': ['megan-precision5550']}]},
                        'host_file_content_2': {'host.present': [{'ip': '::1'}, {'names': ['localhost', 'ip6-localhost', 'ip6-loopback']}]},
                        'host_file_content_3': {'host.present': [{'ip': 'ff02::1'}, {'names': ['ip6-allnodes']}]},
                        'host_file_content_4': {'host.present': [{'ip': 'ff02::2'}, {'names': ['ip6-allrouters']}]}}

    host_file = tmp_path / "poc-minion" / "host.sls"
    with patch.dict(
        salt_describe_runner.__salt__, {"salt.execute": MagicMock(return_value=host_list)}
    ):
        with patch.dict(
            salt_describe_runner.__salt__,
            {"config.get": MagicMock(return_value=[tmp_path])},
        ):
            assert salt_describe_runner.host("minion") == True
            with open(host_file, "r") as fp:
                content = yaml.safe_load(fp.read())
                assert content == expected_content
