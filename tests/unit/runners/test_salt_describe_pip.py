import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.salt_describe.runners.salt_describe_pip as salt_describe_pip_runner
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_pip_runner: {
            "__salt__": {"salt.execute": MagicMock()},
            "__opts__": {},
        },
    }


def test_pip():
    pip_list = {
        "minion": [
            "requests==0.1.2",
            "salt==3004.1",
            "argcomplete==2.3.4-5",
        ],
    }

    expected_sls_write = yaml.dump(
        {
            "installed_pip_libraries": {"pip.installed": [{"pkgs": pip_list["minion"]}]},
        }
    )
    with patch.dict(
        salt_describe_pip_runner.__salt__, {"salt.execute": MagicMock(return_value=pip_list)}
    ):
        with patch.object(salt_describe_pip_runner, "generate_files") as generate_mock:
            assert salt_describe_pip_runner.pip("minion") is True
            generate_mock.assert_called_with(
                {}, "minion", expected_sls_write, sls_name="pip", config_system="salt"
            )