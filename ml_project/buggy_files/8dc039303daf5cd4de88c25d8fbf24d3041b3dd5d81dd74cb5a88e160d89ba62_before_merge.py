def ensure_linked_actions(dists, prefix, index=None, force=False,
                          always_copy=False, shortcuts=False):
    actions = defaultdict(list)
    actions[inst.PREFIX] = prefix
    actions['op_order'] = (inst.RM_FETCHED, inst.FETCH, inst.RM_EXTRACTED,
                           inst.EXTRACT, inst.UNLINK, inst.LINK)
    for dist in dists:
        fetched_in = is_fetched(dist)
        extracted_in = is_extracted(dist)

        if fetched_in and index is not None:
            # Test the MD5, and possibly re-fetch
            fn = dist + '.tar.bz2'
            try:
                if md5_file(fetched_in) != index[fn]['md5']:
                    # RM_FETCHED now removes the extracted data too
                    actions[inst.RM_FETCHED].append(dist)
                    # Re-fetch, re-extract, re-link
                    fetched_in = extracted_in = None
                    force = True
            except KeyError:
                sys.stderr.write('Warning: cannot lookup MD5 of: %s' % fn)

        if not force and is_linked(prefix, dist):
            continue

        if extracted_in and force:
            # Always re-extract in the force case
            actions[inst.RM_EXTRACTED].append(dist)
            extracted_in = None

        # Otherwise we need to extract, and possibly fetch
        if not extracted_in and not fetched_in:
            # If there is a cache conflict, clean it up
            fetched_in, conflict = find_new_location(dist)
            fetched_in = join(fetched_in, dist2filename(dist))
            if conflict is not None:
                actions[inst.RM_FETCHED].append(conflict)
            actions[inst.FETCH].append(dist)

        if not extracted_in:
            actions[inst.EXTRACT].append(dist)

        fetched_dist = extracted_in or fetched_in[:-8]
        fetched_dir = dirname(fetched_dist)

        try:
            # Determine what kind of linking is necessary
            if not extracted_in:
                # If not already extracted, create some dummy
                # data to test with
                rm_rf(fetched_dist)
                ppath = join(fetched_dist, 'info')
                os.makedirs(ppath)
                index_json = join(ppath, 'index.json')
                with open(index_json, 'w'):
                    pass
            if config_always_copy or always_copy:
                lt = LINK_COPY
            elif try_hard_link(fetched_dir, prefix, dist):
                lt = LINK_HARD
            elif allow_softlinks and sys.platform != 'win32':
                lt = LINK_SOFT
            else:
                lt = LINK_COPY
            actions[inst.LINK].append('%s %d %s' % (dist, lt, shortcuts))

        except (OSError, IOError):
            actions[inst.LINK].append(dist, LINK_COPY, shortcuts)
        finally:
            if not extracted_in:
                # Remove the dummy data
                try:
                    rm_rf(fetched_dist)
                except (OSError, IOError):
                    pass

    return actions