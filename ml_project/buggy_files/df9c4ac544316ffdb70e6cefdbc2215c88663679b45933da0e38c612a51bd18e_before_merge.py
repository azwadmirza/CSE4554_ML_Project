    def build_map(master, state, uricache):
        tmap = {}
        for topic, ttype, tnodes in state:
            for p in tnodes:
                if not p in uricache:
                   uricache[p] = master.lookupNode(p)
                uri = uricache[p]
                puri = urlparse(uri)
                if not puri.hostname in tmap:
                    tmap[puri.hostname] = []
                # recreate the system state data structure, but for a single host
                matches = [l for x, l in tmap[puri.hostname] if x == topic]
                if matches:
                    matches[0].append(p)
                else:
                    tmap[puri.hostname].append((topic, [p]))
        return tmap