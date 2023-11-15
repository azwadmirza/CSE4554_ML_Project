    def __init__(self, provider: str, path: str):
        super().__init__(provider=provider, path=path)
        self.headers: Dict[str, Dict[str, str]] = {
            "package_test/explicit.yaml": {"package": "a.b"},
            "package_test/global.yaml": {"package": "_global_"},
            "package_test/group.yaml": {"package": "_group_"},
            "package_test/group_name.yaml": {"package": "foo._group_._name_"},
            "package_test/name.yaml": {"package": "_name_"},
            "package_test/none.yaml": {},
            "primary_config_with_non_global_package.yaml": {"package": "foo"},
        }
        self.configs: Dict[str, Dict[str, Any]] = {
            "primary_config.yaml": {"primary": True},
            "primary_config_with_non_global_package.yaml": {"primary": True},
            "config_without_group.yaml": {"group": False},
            "config_with_unicode.yaml": {"group": "数据库"},
            "dataset/imagenet.yaml": {
                "dataset": {"name": "imagenet", "path": "/datasets/imagenet"}
            },
            "dataset/cifar10.yaml": {
                "dataset": {"name": "cifar10", "path": "/datasets/cifar10"}
            },
            "level1/level2/nested1.yaml": {"l1_l2_n1": True},
            "level1/level2/nested2.yaml": {"l1_l2_n2": True},
            "package_test/explicit.yaml": {"foo": "bar"},
            "package_test/global.yaml": {"foo": "bar"},
            "package_test/group.yaml": {"foo": "bar"},
            "package_test/group_name.yaml": {"foo": "bar"},
            "package_test/name.yaml": {"foo": "bar"},
            "package_test/none.yaml": {"foo": "bar"},
        }