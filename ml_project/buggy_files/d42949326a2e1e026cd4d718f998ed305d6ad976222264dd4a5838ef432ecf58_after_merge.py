    def _set_center(self, center):
        if center is None:
            self.center = None
            return
        elif isinstance(center, YTArray):
            self.center = self.ds.arr(center.astype("float64"))
            self.center.convert_to_units("code_length")
        elif isinstance(center, (list, tuple, np.ndarray)):
            if isinstance(center[0], YTQuantity):
                self.center = self.ds.arr([c.copy() for c in center], dtype="float64")
                self.center.convert_to_units("code_length")
            else:
                self.center = self.ds.arr(center, "code_length", dtype="float64")
        elif isinstance(center, str):
            if center.lower() in ("c", "center"):
                self.center = self.ds.domain_center
            # is this dangerous for race conditions?
            elif center.lower() in ("max", "m"):
                self.center = self.ds.find_max(("gas", "density"))[1]
            elif center.startswith("max_"):
                self.center = self.ds.find_max(center[4:])[1]
            elif center.lower() == "min":
                self.center = self.ds.find_min(("gas", "density"))[1]
            elif center.startswith("min_"):
                self.center = self.ds.find_min(center[4:])[1]
        else:
            self.center = self.ds.arr(center, "code_length", dtype="float64")

        if self.center.ndim > 1:
            mylog.debug("Removing singleton dimensions from 'center'.")
            self.center = np.squeeze(self.center)
            if self.center.ndim > 1:
                msg = (
                    "center array must be 1 dimensional, supplied center has "
                    f"{self.center.ndim} dimensions with shape {self.center.shape}."
                )
                raise YTException(msg)

        self.set_field_parameter("center", self.center)