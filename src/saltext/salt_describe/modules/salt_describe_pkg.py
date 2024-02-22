# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for building state file

.. versionadded:: 1.1.0

"""
import logging
import sys

import salt.utils.minions  # pylint: disable=import-error
import yaml
from saltext.salt_describe.utils.init import generate_files
from saltext.salt_describe.utils.init import parse_salt_ret
from saltext.salt_describe.utils.init import ret_info
from saltext.salt_describe.utils.pkg import _parse_ansible
from saltext.salt_describe.utils.pkg import _parse_chef
from saltext.salt_describe.utils.pkg import _parse_salt


__virtualname__ = "describe"


log = logging.getLogger(__name__)


def __virtual__():
    return __virtualname__


def pkg(include_version=True, single_state=True, config_system="salt", **kwargs):
    """
    Gather installed pkgs on minions and build a state file.

    CLI Example:

    .. code-block:: bash

        salt-run describe.pkg

        salt-run describe.pkg config_system=ansible

        salt-run describe.pkg config_system=chef
    """
    ret = {}
    mod_name = sys._getframe().f_code.co_name
    log.info("Attempting to generate SLS file for %s", mod_name)
    minion = __salt__["config.get"]("id")
    ret[minion] = __salt__["pkg.list_pkgs"]()

    sls_files = []
    if not parse_salt_ret(ret=ret, tgt=minion):
        return ret_info(sls_files, mod=mod_name)

    _, grains, _ = salt.utils.minions.get_minion_data(minion, __opts__)

    pkg_cmd = None
    if config_system == "ansible":
        if grains["os_family"] not in ("Debian", "RedHat"):
            log.debug("Unsupported minion")
            return False
        else:
            if grains["os_family"] in ("Debian",):
                pkg_cmd = "apt"
            elif grains["os_family"] in ("RedHat"):
                pkg_cmd = "dnf"

    pkgs = ret[minion]
    state_contents = getattr(sys.modules[__name__], f"_parse_{config_system}")(
        minion, pkgs, single_state, include_version, pkg_cmd, **kwargs
    )

    if config_system in ("ansible", "salt"):
        state = yaml.dump(state_contents)
    else:
        state = "\n".join(state_contents)

    sls_files.append(
        generate_files(__opts__, minion, state, sls_name="pkg", config_system=config_system)
    )

    return ret_info(sls_files, mod=mod_name)
