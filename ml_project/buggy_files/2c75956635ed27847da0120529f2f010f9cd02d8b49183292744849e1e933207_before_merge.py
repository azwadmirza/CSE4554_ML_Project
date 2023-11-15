    def inventory_path(self):
        return os.path.join(DEFAULT_CONFIG_ROOT, NODE_CONFIG_STORAGE_KEY, f'{self.namespace_network}.ansible_inventory.yml')