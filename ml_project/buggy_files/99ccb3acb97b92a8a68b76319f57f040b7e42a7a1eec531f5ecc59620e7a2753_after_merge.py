    def branch_relatives(self, branch):
        # type: (str) -> List[str]
        """ Get list of all relatives from ``git show-branch`` results """
        output = self.git("show-branch", "--no-color")  # type: str

        try:
            prelude, body = re.split(r'^-+$', output, flags=re.M)
        except ValueError:
            # If there is only one branch, git changes the output format
            # and omits the prelude and column indicator.
            lines = filter(None, output.splitlines())
        else:
            match = re.search(r'^(\s+)\*', prelude, re.M)
            if not match:
                print("branch {} not found in header information".format(branch))
                return []

            branch_column = len(match.group(1))
            lines = (
                line
                for line in filter(None, body.splitlines())
                if line[branch_column] != ' '
            )

        relatives = []  # type: List[str]
        for line in lines:
            match = EXTRACT_BRANCH_NAME.match(line)
            if match:
                branch_name = match.group(1)
                if branch_name != branch and branch_name not in relatives:
                    relatives.append(branch_name)

        return relatives