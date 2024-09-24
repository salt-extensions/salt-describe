# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for building state file

.. versionadded:: 3006.0

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


def beacon(tgt, tgt_type="glob", config_system="salt"):
    """
    Generate the state file for a Salt beacon data

    CLI Example:

    .. code-block:: bash

        salt-run describe.beacon minion-tgt
    """
    describe_config = __opts__.get("describe", {})

    mod_name = sys._getframe().f_code.co_name
    log.info("Attempting to generate SLS file for %s", mod_name)
    beacon_contents = __salt__["salt.execute"](
        tgt,
        "beacons.list",
        tgt_type=tgt_type,
        kwarg={"return_yaml": False},
    )
    sls_files = []
    if not parse_salt_ret(ret=beacon_contents, tgt=tgt):
        return ret_info(sls_files, mod=mod_name)
    for minion in list(beacon_contents.keys()):
        minion_beacons = beacon_contents[minion]

        beacons_sls = {}
        for beacon in minion_beacons.keys():
            # Generate beacons state
            beacon_state_name = beacon
            beacon_state = {
                "beacon.present": minion_beacons[beacon],
            }

            beacons_sls[beacon_state_name] = beacon_state

        sls_yaml = yaml.dump(beacons_sls)
        sls_files.append(
            generate_files(
                __opts__, minion, sls_yaml, sls_name="beacon", config_system=config_system
            )
        )

    return ret_info(sls_files, mod=mod_name)
