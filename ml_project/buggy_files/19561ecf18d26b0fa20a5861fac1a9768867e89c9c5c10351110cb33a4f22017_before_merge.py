    def debug_choose_group(self, index):
        self.__grouping_index = index
        self.__within_group_index = 0
        workspace = cellprofiler.gui.workspace.Workspace(
            self.__pipeline,
            None,
            None,
            None,
            self.__debug_measurements,
            self.__debug_image_set_list,
            self.__frame,
        )

        self.__pipeline.prepare_group(
            workspace,
            self.__groupings[self.__grouping_index][0],
            self.__groupings[self.__grouping_index][1],
        )
        key, image_numbers = self.__groupings[self.__grouping_index]
        image_number = image_numbers[self.__within_group_index]
        self.__debug_measurements.next_image_set(image_number)
        self.__pipeline_list_view.reset_debug_module()
        self.__debug_outlines = {}