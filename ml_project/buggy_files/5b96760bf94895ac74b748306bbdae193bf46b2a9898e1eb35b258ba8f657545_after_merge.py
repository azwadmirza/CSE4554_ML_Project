    def from_url(cls, url: str) -> Optional['YukicoderProblem']:
        # example: https://yukicoder.me/problems/no/499
        # example: http://yukicoder.me/problems/1476
        result = urllib.parse.urlparse(url)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            n = None  # type: Optional[int]
            try:
                n = int(basename)
            except ValueError:
                pass
            if n is not None:
                if dirname == '/problems/no':
                    return cls(problem_no=n)
                if dirname == '/problems':
                    return cls(problem_id=n)
        return None