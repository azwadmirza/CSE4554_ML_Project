    def data(self):
        """
        Return a data container configured like the original used to
        create this dataset.
        """

        if self._data_obj is None:
            # Some data containers can't be recontructed in the same way
            # since this is now particle-like data.
            data_type = self.parameters.get("data_type")
            container_type = self.parameters.get("container_type")
            ex_container_type = ["cutting", "proj", "ray", "slice", "cut_region"]
            if data_type == "yt_light_ray" or container_type in ex_container_type:
                mylog.info("Returning an all_data data container.")
                return self.all_data()

            my_obj = getattr(self, self.parameters["container_type"])
            my_args = [self.parameters[con_arg]
                       for con_arg in self.parameters["con_args"]]
            self._data_obj = my_obj(*my_args)
        return self._data_obj