    def __init__(
        self,
        reddit: "Reddit",
        subreddit: Optional["Subreddit"] = None,
        short_name: Optional[str] = None,
        _data: Optional[Dict[str, str]] = None,
    ):
        """Construct an instance of the Rule object."""
        if (short_name, _data).count(None) != 1:
            raise ValueError("Either short_name or _data needs to be given.")
        if short_name:
            self.short_name = short_name
        # Note: The subreddit parameter can be None, because the objector does not know
        # this info. In that case, it is the responsibility of the caller to set the
        # `subreddit` property on the returned value.
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data)