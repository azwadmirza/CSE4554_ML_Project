    def get_user_requests(self):
        """
        return a list of user requested items.  Each item is a dict with the
        following keys:
        'date': the date and time running the command
        'cmd': a list of argv of the actual command which was run
        'action': install/remove/update
        'specs': the specs being used
        """
        res = []
        for dt, unused_cont, comments in self.parse():
            item = {'date': dt}
            for line in comments:
                comment_items = self._parse_comment_line(line)
                item.update(comment_items)

            if 'cmd' in item:
                res.append(item)

            dists = groupby(itemgetter(0), unused_cont)
            item['unlink_dists'] = dists.get('-', ())
            item['link_dists'] = dists.get('+', ())

        return res