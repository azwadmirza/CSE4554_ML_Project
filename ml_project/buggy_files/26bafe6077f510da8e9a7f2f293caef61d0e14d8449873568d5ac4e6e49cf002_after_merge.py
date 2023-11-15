    def get_announcements(self, courses, **kwargs):
        """
        List announcements.

        :calls: `GET /api/v1/announcements \
        <https://canvas.instructure.com/doc/api/announcements.html#method.announcements_api.index>`_

        :param courses: Course ID(s) or <Course> objects to request announcements from.
        :type courses: list

        :rtype: :class:`canvasapi.paginated_list.PaginatedList` of
                :class:`canvasapi.discussion_topic.DiscussionTopic`
        """
        from canvasapi.discussion_topic import DiscussionTopic

        if type(courses) is not list or len(courses) == 0:
            raise RequiredFieldMissing("Course IDs need to be passed as a list")

        # The type of object in `courses` is taken care of by obj_or_id, extracting the couse
        # ID from a <Course> object or by returning plain strings.
        course_ids = [
            obj_or_id(course_id, "course_id", (Course,)) for course_id in courses
        ]

        # Set the **kwargs object vaue so it can be combined with others passed by the user.
        kwargs["context_codes"] = [f"course_{course_id}" for course_id in course_ids]

        return PaginatedList(
            DiscussionTopic,
            self.__requester,
            "GET",
            "announcements",
            context_codes=course_ids,
            _kwargs=combine_kwargs(**kwargs),
        )