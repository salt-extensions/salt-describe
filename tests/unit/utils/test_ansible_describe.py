# Copyright 2024 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#

import yaml

import saltext.salt_describe.utils.ansible_describe as ansible_describe_util


def test_generate_files(tmp_path):
    yml_contents = [
        {
            "tasks": [
                {
                    "ansible.builtin.service": {"state": "started", "name": "apache2"},
                    "name": "Start service apache",
                }
            ],
            "hosts": "localhost",
            "name": "Manage Service",
        }
    ]

    yml = yaml.dump(yml_contents)
    root = tmp_path / "ansible" / "minion"
    yml_file = root / "file.yml"
    assert (
        ansible_describe_util.generate_files(
            {}, "minion", yml, sls_name="file", env="prod", root=tmp_path
        )
        == yml_file
    )
    assert yml_file.exists()
    assert yaml.safe_load(yml_file.read_text()) == yml_contents
