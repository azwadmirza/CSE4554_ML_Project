    def teardown_handles(self):
        box_artists = ('cmedians', 'cmeans', 'cmaxes', 'cmins', 'cbars', 'bodies')
        violin_artists = ('whiskers', 'fliers', 'medians', 'boxes', 'caps', 'means')
        for group in box_artists+violin_artists:
            for v in self.handles.get(group, []):
                v.remove()