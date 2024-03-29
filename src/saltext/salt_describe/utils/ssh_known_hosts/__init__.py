# Copyright 2023-2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

log = logging.getLogger(__name__)


def _parse_salt(minion, user_keys, **kwargs):
    """
    Parse the returned ssh_known_hosts commands and return
    salt data.
    """
    state_contents = {}
    for user in user_keys:
        for key in user_keys[user]:
            data = user_keys[user][key]
            ssh_auth_present = [{"user": user}, {"enc": data["enc"]}]

            if data.get("options"):
                ssh_auth_present.append({"options": data["options"]})
            if data.get("comment"):
                ssh_auth_present.append({"comment": data["comment"]})

            state_contents[key] = {"ssh_auth.present": ssh_auth_present}

    return state_contents


def _parse_ansible(minion, user_keys, **kwargs):
    """
    Parse the returned service commands and return
    ansible data.
    """
    data = {}
    data = {"name": "Manage SSH Auth Keys", "tasks": []}
    if not kwargs.get("hosts"):
        log.error(
            "Hosts was not passed. You will need to manually edit the playbook with the hosts entry"
        )
    else:
        data["hosts"] = kwargs.get("hosts")
    state_contents = []

    for user in user_keys:
        for key in user_keys[user]:
            key_data = user_keys[user][key]

            ssh_auth_data = {"user": user, "key": key}

            if key_data.get("options"):
                ssh_auth_data["key_options"] = ", ".join(key_data["options"])

            data["tasks"].append(
                {
                    "name": f"Manage ssh-auth key {key}",
                    "ansible.posix.authorized_key": ssh_auth_data,
                }
            )
        state_contents.append(data)
    return state_contents


def _parse_chef(minion, user_keys, **kwargs):
    """
    Parse the returned service commands and return
    chef data.
    """
    _contents = []

    _contents.append("depends 'ssh_authorized_keys'")
    for user in user_keys:
        for key in user_keys[user]:
            data = user_keys[user][key]

            service_template = f"""ssh_authorize_key '{user}' do
  key '{key}'
  user '{user}'
"""
            if data.get("options"):
                service_template += "  options(\n"
                for _option in data["options"]:
                    _option_key, _option_value = _option.split("=")
                    service_template += f"    '{_option_key}' => '{_option_value}',\n"
                service_template += "  )\n"

            service_template += "end\n"

            _contents.append(service_template)
    return _contents
