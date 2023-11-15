def get_reduced_index(prefix, channels, subdirs, specs):

    # # this block of code is a "combine" step intended to filter out redundant specs
    # # causes a problem with py.test tests/core/test_solve.py -k broken_install
    # specs_map = defaultdict(list)
    # for spec in specs:
    #     specs_map[spec.name].append(spec)
    # consolidated_specs = set()
    # for spec_name, specs_group in iteritems(specs_map):
    #     if len(specs_group) == 1:
    #         consolidated_specs.add(specs_group[0])
    #     elif spec_name == '*':
    #         consolidated_specs.update(specs_group)
    #     else:
    #         keep_specs = []
    #         for spec in specs_group:
    #             if len(spec._match_components) > 1 or spec.target or spec.optional:
    #                 keep_specs.append(spec)
    #         consolidated_specs.update(keep_specs)

    with ThreadLimitedThreadPoolExecutor() as executor:

        channel_urls = all_channel_urls(channels, subdirs=subdirs)
        check_whitelist(channel_urls)

        if context.offline:
            grouped_urls = groupby(lambda url: url.startswith('file://'), channel_urls)
            ignored_urls = grouped_urls.get(False, ())
            if ignored_urls:
                log.info("Ignoring the following channel urls because mode is offline.%s",
                         dashlist(ignored_urls))
            channel_urls = IndexedSet(grouped_urls.get(True, ()))
        subdir_datas = tuple(SubdirData(Channel(url)) for url in channel_urls)

        records = IndexedSet()
        collected_names = set()
        collected_track_features = set()
        pending_names = set()
        pending_track_features = set()

        def query_all(spec):
            futures = tuple(executor.submit(sd.query, spec) for sd in subdir_datas)
            return tuple(concat(future.result() for future in as_completed(futures)))

        def push_spec(spec):
            name = spec.get_raw_value('name')
            if name and name not in collected_names:
                pending_names.add(name)
            track_features = spec.get_raw_value('track_features')
            if track_features:
                for ftr_name in track_features:
                    if ftr_name not in collected_track_features:
                        pending_track_features.add(ftr_name)

        def push_record(record):
            push_spec(MatchSpec(record.name))
            for _spec in record.combined_depends:
                push_spec(_spec)
            if record.track_features:
                for ftr_name in record.track_features:
                    push_spec(MatchSpec(track_features=ftr_name))

        if prefix:
            for prefix_rec in PrefixData(prefix).iter_records():
                push_record(prefix_rec)
        for spec in specs:
            push_spec(spec)

        while pending_names or pending_track_features:
            while pending_names:
                name = pending_names.pop()
                collected_names.add(name)
                spec = MatchSpec(name)
                new_records = query_all(spec)
                for record in new_records:
                    push_record(record)
                records.update(new_records)

            while pending_track_features:
                feature_name = pending_track_features.pop()
                collected_track_features.add(feature_name)
                spec = MatchSpec(track_features=feature_name)
                new_records = query_all(spec)
                for record in new_records:
                    push_record(record)
                records.update(new_records)

        reduced_index = {Dist(rec): rec for rec in records}

        if prefix is not None:
            _supplement_index_with_prefix(reduced_index, prefix)

        if context.offline or ('unknown' in context._argparse_args
                               and context._argparse_args.unknown):
            # This is really messed up right now.  Dates all the way back to
            # https://github.com/conda/conda/commit/f761f65a82b739562a0d997a2570e2b8a0bdc783
            # TODO: revisit this later
            _supplement_index_with_cache(reduced_index)

        # add feature records for the solver
        known_features = set()
        for rec in itervalues(reduced_index):
            known_features.update(concatv(rec.track_features, rec.features))
        known_features.update(context.track_features)
        for ftr_str in known_features:
            rec = make_feature_record(ftr_str)
            reduced_index[Dist(rec)] = rec

        return reduced_index