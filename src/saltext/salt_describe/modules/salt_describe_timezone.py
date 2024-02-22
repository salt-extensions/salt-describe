# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for building state file

.. versionadded:: 1.1.0

"""
import logging
import sys

import yaml
from saltext.salt_describe.utils.init import generate_files
from saltext.salt_describe.utils.init import parse_salt_ret
from saltext.salt_describe.utils.init import ret_info

__virtualname__ = "describe"


log = logging.getLogger(__name__)


def __virtual__():
    return __virtualname__


def timezone(config_system="salt"):
    """
    Gather the timezone data for minions and generate a state file.

    CLI Example:

    .. code-block:: bash

        salt-run describe.timezone minion-tgt

    """
    mod_name = sys._getframe().f_code.co_name
    log.info("Attempting to generate SLS file for %s", mod_name)
    minion_id = __salt__["config.get"]("id")
    timezones = {minion_id: __salt__["timezone.get_zone"]()}

    sls_files = []
    if not parse_salt_ret(ret=timezones, tgt=minion_id):
        return ret_info(sls_files, mod=mod_name)

    for minion in list(timezones.keys()):
        timezone = timezones[minion]

        state_contents = {}
        state_contents = {timezone: {"timezone.system": []}}

        state = yaml.dump(state_contents)

        sls_files.append(
            generate_files(
                __opts__, minion, state, sls_name="timezone", config_system=config_system
            )
        )

    return ret_info(sls_files, mod=mod_name)
