    def id_from_url(url: str) -> str:
        """Return the ID contained within a submission URL.

        :param url: A url to a submission in one of the following formats (http urls
            will also work):

            * https://redd.it/2gmzqe
            * https://reddit.com/comments/2gmzqe/
            * https://www.reddit.com/r/redditdev/comments/2gmzqe/praw_https/
            * https://www.reddit.com/gallery/2gmzqe

        :raises: :class:`.InvalidURL` if URL is not a valid submission URL.

        """
        parts = RedditBase._url_parts(url)
        if "comments" not in parts and "gallery" not in parts:
            submission_id = parts[-1]
            if "r" in parts:
                raise InvalidURL(
                    url, message="Invalid URL (subreddit, not submission): {}"
                )
        elif "gallery" in parts:
            submission_id = parts[parts.index("gallery") + 1]
        else:
            submission_id = parts[parts.index("comments") + 1]

        if not submission_id.isalnum():
            raise InvalidURL(url)
        return submission_id