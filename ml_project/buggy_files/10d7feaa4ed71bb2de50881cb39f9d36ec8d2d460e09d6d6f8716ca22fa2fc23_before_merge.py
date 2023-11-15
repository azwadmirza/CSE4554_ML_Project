    def _parent_id(self):
        """
        Return the id of the course or group that spawned this discussion topic.

        :rtype: int
        """
        if hasattr(self, "course_id"):
            return self.course_id
        elif hasattr(self, "group_id"):
            return self.group_id
        else:
            raise ValueError("Discussion Topic does not have a course_id or group_id")