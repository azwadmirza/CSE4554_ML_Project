    def fetch(self):
        """Fetch the stored value and std attributes.


        See Also
        --------
        store_current_value_in_array, assign_current_value_to_all

        """
        indices = self._axes_manager.indices[::-1]
        # If it is a single spectrum indices is ()
        if not indices:
            indices = (0,)
        if self.map['is_set'][indices]:
            self.value = self.map['values'][indices]
            self.std = self.map['std'][indices]