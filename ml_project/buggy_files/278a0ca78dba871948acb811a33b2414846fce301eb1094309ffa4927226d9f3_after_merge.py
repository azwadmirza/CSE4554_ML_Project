    def _parent_type(self):
        """
        Return whether the discussion topic was spawned from a course or group.

        :rtype: str
        """
        if hasattr(self, "course_id"):
            return "course"
        elif hasattr(self, "group_id"):
            return "group"
        elif hasattr(self, "context_code"):
            if self.context_code.startswith("course"):
                return "course"
            elif self.context_code.startswith("group"):
                return "group"
        else:
            raise ValueError("Discussion Topic does not have a course_id or group_id")