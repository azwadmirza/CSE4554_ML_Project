    def inventory_path(self):
        return str(Path(DEFAULT_CONFIG_ROOT).joinpath(NODE_CONFIG_STORAGE_KEY, f'{self.namespace_network}.ansible_inventory.yml'))