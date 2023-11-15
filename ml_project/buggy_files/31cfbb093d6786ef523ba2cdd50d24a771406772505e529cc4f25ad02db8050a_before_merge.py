    def children(self, recursive=False):
        """Return the children of this process as a list of Process
        instances, pre-emptively checking whether PID has been reused.
        If recursive is True return all the parent descendants.

        Example (A == this process):

         A ─┐
            │
            ├─ B (child) ─┐
            │             └─ X (grandchild) ─┐
            │                                └─ Y (great grandchild)
            ├─ C (child)
            └─ D (child)

        >>> import psutil
        >>> p = psutil.Process()
        >>> p.children()
        B, C, D
        >>> p.children(recursive=True)
        B, X, Y, C, D

        Note that in the example above if process X disappears
        process Y won't be listed as the reference to process A
        is lost.
        """
        if hasattr(_psplatform, 'ppid_map'):
            # Windows only: obtain a {pid:ppid, ...} dict for all running
            # processes in one shot (faster).
            ppid_map = _psplatform.ppid_map()
        else:
            ppid_map = None

        ret = []
        if not recursive:
            if ppid_map is None:
                # 'slow' version, common to all platforms except Windows
                for p in process_iter():
                    try:
                        if p.ppid() == self.pid:
                            # if child happens to be older than its parent
                            # (self) it means child's PID has been reused
                            if self.create_time() <= p.create_time():
                                ret.append(p)
                    except NoSuchProcess:
                        pass
            else:
                # Windows only (faster)
                for pid, ppid in ppid_map.items():
                    if ppid == self.pid:
                        try:
                            child = Process(pid)
                            # if child happens to be older than its parent
                            # (self) it means child's PID has been reused
                            if self.create_time() <= child.create_time():
                                ret.append(child)
                        except NoSuchProcess:
                            pass
        else:
            # construct a dict where 'values' are all the processes
            # having 'key' as their parent
            table = collections.defaultdict(list)
            if ppid_map is None:
                for p in process_iter():
                    try:
                        table[p.ppid()].append(p)
                    except NoSuchProcess:
                        pass
            else:
                for pid, ppid in ppid_map.items():
                    try:
                        p = Process(pid)
                        table[ppid].append(p)
                    except NoSuchProcess:
                        pass
            # At this point we have a mapping table where table[self.pid]
            # are the current process' children.
            # Below, we look for all descendants recursively, similarly
            # to a recursive function call.
            checkpids = [self.pid]
            for pid in checkpids:
                for child in table[pid]:
                    try:
                        # if child happens to be older than its parent
                        # (self) it means child's PID has been reused
                        intime = self.create_time() <= child.create_time()
                    except NoSuchProcess:
                        pass
                    else:
                        if intime:
                            ret.append(child)
                            if child.pid not in checkpids:
                                checkpids.append(child.pid)
        return ret