    def __init__(
        self,
        element,
        order_by=None,
        partition_by=None,
        preceding=None,
        following=None,
    ):
        super().__init__(element, order_by=order_by, partition_by=partition_by)
        if not isinstance(preceding, _valid_frame_types):
            raise TypeError(
                'preceding must be a string, integer or None, got %r'
                % (type(preceding).__name__)
            )
        if not isinstance(following, _valid_frame_types):
            raise TypeError(
                'following must be a string, integer or None, got %r'
                % (type(following).__name__)
            )
        self.preceding = preceding if preceding is not None else 'UNBOUNDED'
        self.following = following if following is not None else 'UNBOUNDED'