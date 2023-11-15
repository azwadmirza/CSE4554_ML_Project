    def push_MatchSpec(self, C, spec):
        spec = MatchSpec(spec)
        sat_name = self.to_sat_name(spec)
        m = C.from_name(sat_name)
        if m is not None:
            # the spec has already been pushed onto the clauses stack
            return sat_name

        simple = spec._is_single()
        nm = spec.get_exact_value('name')
        tf = spec.get_exact_value('track_features')

        if nm:
            tgroup = libs = self.groups.get(nm, [])
        elif tf:
            assert len(tf) == 1
            k = next(iter(tf))
            tgroup = libs = self.trackers.get(k, [])
        else:
            tgroup = libs = self.index.keys()
            simple = False
        if not simple:
            libs = [fkey for fkey in tgroup if self.match(spec, fkey)]
        if len(libs) == len(tgroup):
            if spec.optional:
                m = True
            elif not simple:
                ms2 = MatchSpec(track_features=tf) if tf else MatchSpec(nm)
                m = C.from_name(self.push_MatchSpec(C, ms2))
        if m is None:
            dists = [dist.full_name for dist in libs]
            if spec.optional:
                ms2 = MatchSpec(track_features=tf) if tf else MatchSpec(nm)
                dists.append('!' + self.to_sat_name(ms2))
            m = C.Any(dists)
        C.name_var(m, sat_name)
        return sat_name