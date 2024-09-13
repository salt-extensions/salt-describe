# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import locale

import pytest
import salt.grains.core as core_grains
import yaml


@pytest.mark.skipif(
    core_grains.saltversion()["saltversion"] == "3006.9",
    reason="Fails because of old requirements on 3006.x",
)
def test_pip(salt_run_cli, minion):
    """
    Test describe.pip
    """
    ret = salt_run_cli.run("describe.pip", tgt=minion.id)
    gen_sls = ret.data["Generated SLS file locations"][0]
    with open(gen_sls, encoding=locale.getpreferredencoding()) as fp:
        data = yaml.safe_load(fp)
    assert "pkgs" in data["installed_pip_libraries"]["pip.installed"][0]
    assert ret.returncode == 0
