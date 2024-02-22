# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

log = logging.getLogger(__name__)


def _parse_salt(minion, pkgs, single_state, include_version, pkg_cmd, **kwargs):
    """
    Parse the returned pkg commands and return
    salt data.
    """
    if single_state:
        if include_version:
            _pkgs = [{name: version} for name, version in pkgs.items()]
        else:
            _pkgs = list(pkgs.keys())

        state_contents = {"installed_packages": {"pkg.installed": [{"pkgs": _pkgs}]}}
    else:
        state_contents = {}
        for name, version in pkgs.items():
            state_name = f"install_{name}"
            if include_version:
                state_contents[state_name] = {"pkg.installed": [{"name": name, "version": version}]}
            else:
                state_contents[state_name] = {"pkg.installed": [{"name": name}]}
    return state_contents


def _parse_ansible(minion, pkgs, single_state, include_version, pkg_cmd, **kwargs):
    """
    Parse the returned pkg commands and return
    ansible data.
    """
    state_contents = []
    data = {"tasks": []}
    if not kwargs.get("hosts"):
        log.error(
            "Hosts was not passed. You will need to manually edit the playbook with the hosts entry"
        )
    else:
        data["hosts"] = kwargs.get("hosts")
    if single_state:
        _pkgs = list(pkgs.keys())
        data["tasks"].append(
            {
                "name": f"Package Installaion",
                f"{pkg_cmd}": {
                    "name": _pkgs,
                },
            }
        )
    else:
        for name, version in pkgs.items():
            data_name = f"install_{name}"
            if include_version:
                data["tasks"].append(
                    {
                        "name": f"Install package {name}",
                        f"{pkg_cmd}": {
                            "state": version,
                            "name": name,
                        },
                    }
                )
            else:
                data["tasks"].append(
                    {
                        "name": f"Install package {name}",
                        f"{pkg_cmd}": {
                            "name": name,
                        },
                    }
                )
    state_contents.append(data)
    return state_contents


def _parse_chef(minion, pkgs, single_state, include_version, pkg_cmd, **kwargs):
    """
    Parse the returned pkg commands and return
    chef data.
    """

    _contents = []
    for name, version in pkgs.items():
        pkg_template = f"""package '{name}' do
  action :install
end
"""
        _contents.append(pkg_template)
    return _contents
