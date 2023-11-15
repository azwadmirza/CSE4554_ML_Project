    def update_views(self):
        """Default builder fo the stats views.

        The V of MVC
        A dict of dict with the needed information to display the stats.
        Example for the stat xxx:
        'xxx': {'decoration': 'DEFAULT',
                'optional': False,
                'additional': False,
                'splittable': False}
        """
        ret = {}

        if (isinstance(self.get_raw(), list) and
                self.get_raw() is not None and
                self.get_key() is not None):
            # Stats are stored in a list of dict (ex: NETWORK, FS...)
            for i in self.get_raw():
                ret[i[self.get_key()]] = {}
                for key in viewkeys(i):
                    value = {'decoration': 'DEFAULT',
                             'optional': False,
                             'additional': False,
                             'splittable': False}
                    ret[i[self.get_key()]][key] = value
        elif isinstance(self.get_raw(), dict) and self.get_raw() is not None:
            # Stats are stored in a dict (ex: CPU, LOAD...)
            for key in viewkeys(self.get_raw()):
                value = {'decoration': 'DEFAULT',
                         'optional': False,
                         'additional': False,
                         'splittable': False}
                ret[key] = value

        self.views = ret

        return self.views