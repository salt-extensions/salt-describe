# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for building state file

.. versionadded:: 3006

"""
import logging
import sys

import yaml
from saltext.salt_describe.utils.cron import _parse_pre_cron
from saltext.salt_describe.utils.init import generate_files
from saltext.salt_describe.utils.init import parse_salt_ret
from saltext.salt_describe.utils.init import ret_info

__virtualname__ = "describe"


log = logging.getLogger(__name__)


def __virtual__():
    return __virtualname__


def cron(tgt, user="root", include_pre=True, tgt_type="glob", config_system="salt"):
    """
    Generate the state file for a user's cron data

    CLI Example:

    .. code-block:: bash

        salt-run describe.all minion-tgt user
    """
    mod_name = sys._getframe().f_code.co_name
    log.info("Attempting to generate SLS file for %s", mod_name)
    cron_contents = __salt__["salt.execute"](
        tgt,
        "cron.ls",
        arg=[user],
        tgt_type=tgt_type,
    )
    sls_files = []
    if not parse_salt_ret(ret=cron_contents, tgt=tgt):
        return ret_info(sls_files, mod=mod_name)
    for minion in list(cron_contents.keys()):
        minion_crons = cron_contents[minion]
        crons = minion_crons.get("crons", [])
        env = minion_crons.get("env", [])
        pre = minion_crons.get("pre", [])
        special = minion_crons.get("special", [])

        env_sls = {}
        for env_var in env:
            name = env_var["name"]
            value = env_var["value"]
            # Generate env state
            env_state = {
                "cron.env_present": [
                    {"value": value},
                    {"user": user},
                ],
            }
            env_sls[name] = env_state

        crons_sls = {}
        for job in crons:
            # Generate cron state
            cron_state_name = job["cmd"]
            comment = job["comment"] if job["comment"] else None
            cron_state = {
                "cron.present": [
                    {"user": user},
                    {"minute": job["minute"]},
                    {"hour": job["hour"]},
                    {"daymonth": job["daymonth"]},
                    {"month": job["month"]},
                    {"dayweek": job["dayweek"]},
                    {"comment": comment},
                    {"commented": job["commented"]},
                    {"identifier": job["identifier"]},
                ],
            }

            crons_sls[cron_state_name] = cron_state

        specials_sls = {}
        for job in special:
            # Generate special state
            special_state_name = job["cmd"]
            comment = job["comment"] if job["comment"] else None
            special_state = {
                "cron.present": [
                    {"user": user},
                    {"comment": comment},
                    {"commented": job["commented"]},
                    {"identifier": job["identifier"]},
                    {"special": job["spec"]},
                ],
            }
            specials_sls[special_state_name] = special_state

        if include_pre:
            # do some parsing of `pre` into salt-able cron jobs
            for line in pre:
                line = line.lstrip()
                if line:
                    entry_type, name, data = _parse_pre_cron(line, user)
                    if entry_type == "comment":
                        log.debug("Disregarding comment in cron parsing: %s", data)
                    if entry_type == "env":
                        env_sls[name] = {"cron.env_present": data}
                    if entry_type == "cron":
                        crons_sls[name] = {"cron.present": data}
                    if entry_type == "special":
                        specials_sls[name] = {"cron.present": data}

        # Merge them all together
        final_sls = {}
        for sls_contents in (env_sls, crons_sls, specials_sls):
            for state_name in sls_contents:
                final_sls[state_name] = sls_contents[state_name]

        sls_yaml = yaml.dump(final_sls)
        sls_files.append(
            generate_files(__opts__, minion, sls_yaml, sls_name="cron", config_system=config_system)
        )

    return ret_info(sls_files, mod=mod_name)
