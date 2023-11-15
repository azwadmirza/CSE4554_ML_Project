    def get_pipfile_constraint(self):
        """
        Retrieve the version constraint from the pipfile if it is specified there,
        otherwise check the constraints of the parent dependencies and their conflicts.

        :return: An **InstallRequirement** instance representing a version constraint
        """
        if self.is_in_pipfile:
            return self.pipfile_entry.as_ireq()
        return self.constraint_from_parent_conflicts()