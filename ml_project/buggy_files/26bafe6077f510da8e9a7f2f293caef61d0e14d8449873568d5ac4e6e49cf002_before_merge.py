    def get_announcements(self, **kwargs):
        """
        List announcements.

        :calls: `GET /api/v1/announcements \
        <https://canvas.instructure.com/doc/api/announcements.html#method.announcements_api.index>`_

        :rtype: :class:`canvasapi.paginated_list.PaginatedList` of
                :class:`canvasapi.discussion_topic.DiscussionTopic`
        """
        from canvasapi.discussion_topic import DiscussionTopic

        return PaginatedList(
            DiscussionTopic,
            self.__requester,
            "GET",
            "announcements",
            _kwargs=combine_kwargs(**kwargs),
        )