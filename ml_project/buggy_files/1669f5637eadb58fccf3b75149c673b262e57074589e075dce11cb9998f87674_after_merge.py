    def _handle_migrations(self, settings):
        """Migrate older configs to the newest format."""
        # Simple renamed/deleted options
        for name in list(settings):
            if name in configdata.MIGRATIONS.renamed:
                new_name = configdata.MIGRATIONS.renamed[name]
                log.config.debug("Renaming {} to {}".format(name, new_name))
                settings[new_name] = settings[name]
                del settings[name]
                self._mark_changed()
            elif name in configdata.MIGRATIONS.deleted:
                log.config.debug("Removing {}".format(name))
                del settings[name]
                self._mark_changed()

        # tabs.persist_mode_on_change got merged into tabs.mode_on_change
        old = 'tabs.persist_mode_on_change'
        new = 'tabs.mode_on_change'
        if old in settings:
            settings[new] = {}
            for scope, val in settings[old].items():
                if val:
                    settings[new][scope] = 'persist'
                else:
                    settings[new][scope] = 'normal'

            del settings[old]
            self._mark_changed()

        # bindings.default can't be set in autoconfig.yml anymore, so ignore
        # old values.
        if 'bindings.default' in settings:
            del settings['bindings.default']
            self._mark_changed()

        # Option to show favicons only for pinned tabs changed the type of
        # tabs.favicons.show from Bool to String
        name = 'tabs.favicons.show'
        if name in settings:
            for scope, val in settings[name].items():
                if isinstance(val, bool):
                    settings[name][scope] = 'always' if val else 'never'
                    self._mark_changed()

        return settings