    def do_step(self, module, select_next_module=False):
        """Do a debugging step by running a module
        """
        failure = 1
        old_cursor = self.__frame.GetCursor()
        self.__frame.SetCursor(wx.Cursor(wx.CURSOR_WAIT))
        try:
            image_set_number = self.__debug_measurements.image_set_number
            self.__debug_measurements.add_image_measurement(
                GROUP_NUMBER, self.__grouping_index + 1
            )  # in the analysis mode version, it starts at 1
            self.__debug_measurements.add_image_measurement(
                GROUP_INDEX, self.__within_group_index + 1
            )  # in the analysis mode version, it starts at 1
            self.__debug_measurements.add_image_measurement(
                "Group_Length", len(self.__groupings[self.__grouping_index][1])
            )
            workspace_model = cellprofiler.gui._workspace_model.Workspace(
                self.__pipeline,
                module,
                self.__debug_measurements,
                self.__debug_object_set,
                self.__debug_measurements,
                self.__debug_image_set_list,
                self.__frame if module.show_window else None,
                outlines=self.__debug_outlines,
            )
            self.__debug_grids = workspace_model.set_grids(self.__debug_grids)
            cancelled = [False]

            def cancel_handler(cancelled=None):
                if cancelled is None:
                    cancelled = []
                cancelled[0] = True

            workspace_model.cancel_handler = cancel_handler
            self.__pipeline.run_module(module, workspace_model)
            if cancelled[0]:
                self.__frame.SetCursor(old_cursor)
                return False

            if module.show_window:
                fig = workspace_model.get_module_figure(module, image_set_number)
                module.display(workspace_model, fig)
                fig.Refresh()
            workspace_model.refresh()
            if workspace_model.disposition == DISPOSITION_SKIP:
                self.last_debug_module()
            elif (
                module.module_num < len(self.__pipeline.modules())
                and select_next_module
            ):
                self.__pipeline_list_view.select_one_module(module.module_num + 1)
            failure = 0
            if self.workspace_view is not None:
                self.workspace_view.set_workspace(workspace_model)
        except Exception as instance:
            logging.error("Failed to run module %s", module.module_name, exc_info=True)
            event = RunException(instance, module)
            self.__pipeline.notify_listeners(event)
            self.__pipeline_list_view.select_one_module(module.module_num)
            if event.cancel_run:
                self.on_debug_stop(event)
                failure = -1
            failure = 1
        self.__frame.SetCursor(old_cursor)
        if (
            module.module_name != "Restart" or failure == -1
        ) and self.__debug_measurements is not None:
            module_error_measurement = "ModuleError_%02d%s" % (
                module.module_num,
                module.module_name,
            )
            self.__debug_measurements.add_measurement(
                "Image", module_error_measurement, failure
            )
        return failure == 0