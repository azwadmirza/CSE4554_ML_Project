    def populate(self):
        super(Config, self).populate()

        self.facts['config'] = self.responses

        commits = self.responses[1]
        entries = list()
        entry = None

        for line in commits.split('\n'):
            match = re.match(r'(\d+)\s+(.+)by(.+)via(.+)', line)
            if match:
                if entry:
                    entries.append(entry)

                entry = dict(revision=match.group(1),
                             datetime=match.group(2),
                             by=str(match.group(3)).strip(),
                             via=str(match.group(4)).strip(),
                             comment=None)
            else:
                entry['comment'] = line.strip()

        self.facts['commits'] = entries