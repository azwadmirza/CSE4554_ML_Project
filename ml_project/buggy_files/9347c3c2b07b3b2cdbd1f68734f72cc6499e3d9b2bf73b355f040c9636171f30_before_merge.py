    def run(self):
        """
        Run the upgrader if it is enabled in the config.

        Note that by default, upgrading is enabled in the config. It is then disabled
        after upgrading to Tribler 7.
        """
        # Before any upgrade, prepare a separate state directory for the update version so it does not affect the
        # older version state directory. This allows for safe rollback.
        self.version_manager.setup_state_directory_for_upgrade()

        d = self.upgrade_72_to_pony()
        d.addCallback(self.upgrade_pony_db_6to7)
        self.upgrade_config_to_74()
        return d