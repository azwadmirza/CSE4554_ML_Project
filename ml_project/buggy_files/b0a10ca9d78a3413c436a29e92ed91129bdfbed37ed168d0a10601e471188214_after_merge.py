    def run_objects(self, workspace):
        #
        # First, check to see if we should save this image
        #
        if self.when_to_save == WS_FIRST_CYCLE:
            if workspace.measurements[cpmeas.IMAGE, cpmeas.GROUP_INDEX] > 1:
                workspace.display_data.wrote_image = False
                self.save_filename_measurements(workspace)
                return
            
        elif self.when_to_save == WS_LAST_CYCLE:
            workspace.display_data.wrote_image = False
            self.save_filename_measurements( workspace)
            return
        self.save_objects(workspace)