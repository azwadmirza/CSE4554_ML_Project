def _rostopic_list_group_by_host(master, pubs, subs):
    """
    Build up maps for hostname to topic list per hostname
    :returns: publishers host map, subscribers host map, ``{str: set(str)}, {str: set(str)}``
    """
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
                matches = [l for x, _, l in tmap[puri.hostname] if x == topic]
                if matches:
                    matches[0].append(p)
                else:
                    tmap[puri.hostname].append((topic, ttype, [p]))
        return tmap
        
    uricache = {}
    host_pub_topics = build_map(master, pubs, uricache)
    host_sub_topics = build_map(master, subs, uricache)
    return host_pub_topics, host_sub_topics