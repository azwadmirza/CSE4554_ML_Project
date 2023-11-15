    def show_all_tags(self):
        """Show all tags, organized by node."""
        c, tc = self.c, self
        d = {}
        for p in c.all_unique_positions():
            u = p.v.u
            tags = set(u.get(tc.TAG_LIST_KEY, set([])))
            for tag in tags:
                aList = d.get(tag, [])
                aList.append(p.h)
                d [tag] = aList
        # Print all tags.
        for key in sorted(d):
            aList = d.get(key)
            for h in sorted(aList):
                print(f"{key:>8} {h}")