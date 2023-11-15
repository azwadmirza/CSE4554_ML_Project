    def branch_relatives(self, branch):
        # type: (str) -> List[str]
        """ Get list of all relatives from ``git show-branch`` results """
        output = self.git("show-branch", "--no-color")

        prelude, body = re.split(r'^-+$', output, flags=re.M)

        match = re.search(r'^(\s+)\*', prelude, re.M)
        if not match:
            print("branch {} not found in header information".format(branch))
            return []

        branch_column = len(match.group(1))
        relatives = []  # type: List[str]
        for line in filter(None, body.splitlines()):  # type: str
            if line[branch_column] != ' ':
                match = EXTRACT_BRANCH_NAME.match(line)
                if match:
                    branch_name = match.group(1)
                    if branch_name != branch and branch_name not in relatives:
                        relatives.append(branch_name)

        return relatives