    def validate_and_normalize_repo_name(name: str) -> str:
        if not name.isidentifier():
            raise errors.InvalidRepoName("Not a valid Python variable name.")
        return name.lower()