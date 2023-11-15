    def _insert(self, objs):
        """Base method that inserts a set of equivalent objects by modifying
        self.
        """
        assert len(objs) > 1

        inds = tuple(self._get_or_add_ind(x) for x in objs)
        ind = min(inds)

        if config.DEBUG_ARRAY_OPT >= 2:
            print("_insert:", objs, inds)

        if not (ind in self.ind_to_obj):
            self.ind_to_obj[ind] = []

        for i, obj in zip(inds, objs):
            if i == ind:
                if not (obj in self.ind_to_obj[ind]):
                    self.ind_to_obj[ind].append(obj)
                    self.obj_to_ind[obj] = ind
            else:
                if i in self.ind_to_obj:
                    # those already existing are reassigned
                    for x in self.ind_to_obj[i]:
                        self.obj_to_ind[x] = ind
                        self.ind_to_obj[ind].append(x)
                    del self.ind_to_obj[i]
                else:
                    # those that are new are assigned.
                    self.obj_to_ind[obj] = ind
                    self.ind_to_obj[ind].append(obj)