    def on_setting_changed(self, setting, pipeline):
        if (
            setting == self.wants_groups
            and self.wants_groups
            and not self.image_sets_initialized
        ):
            workspace = self.workspace
            self.on_deactivated()
            self.on_activated(workspace)
            needs_prepare_run = False
        else:
            needs_prepare_run = True
        #
        # Unfortunately, test_valid has the side effect of getting
        # the choices set which is why it's called here
        #
        is_valid = True
        for group in self.grouping_metadata:
            try:
                group.metadata_choice.test_valid(pipeline)
            except:
                is_valid = False
        if is_valid:
            if needs_prepare_run:
                result = self.prepare_run(self.workspace)
                if not result:
                    return
            self.update_tables()