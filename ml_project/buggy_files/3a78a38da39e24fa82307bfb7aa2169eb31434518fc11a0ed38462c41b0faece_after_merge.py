def _read_curry_info(curry_paths):
    """Extract info from curry parameter files."""
    curry_params = _read_curry_parameters(curry_paths['info'])
    R = np.eye(4)
    R[[0, 1], [0, 1]] = -1  # rotate 180 deg
    # shift down and back
    # (chosen by eyeballing to make the CTF helmet look roughly correct)
    R[:3, 3] = [0., -0.015, -0.12]
    curry_dev_dev_t = Transform('ctf_meg', 'meg', R)

    # read labels from label files
    label_fname = curry_paths['labels']
    types = ["meg", "eeg", "misc"]
    labels = _read_curry_lines(label_fname,
                               ["LABELS" + CHANTYPES[key] for key in types])
    sensors = _read_curry_lines(label_fname,
                                ["SENSORS" + CHANTYPES[key] for key in types])
    normals = _read_curry_lines(label_fname,
                                ['NORMALS' + CHANTYPES[key] for key in types])
    assert len(labels) == len(sensors) == len(normals)

    all_chans = list()
    for key in ["meg", "eeg", "misc"]:
        chanidx_is_explicit = (len(curry_params.chanidx_in_file["CHAN_IN_FILE"
                                   + CHANTYPES[key]]) > 0)    # channel index
        # position in the datafile may or may not be explicitly declared,
        # based on the CHAN_IN_FILE section in info file
        for ind, chan in enumerate(labels["LABELS" + CHANTYPES[key]]):
            chanidx = len(all_chans) + 1    # by default, just assume the
            # channel index in the datafile is in order of the channel
            # names as we found them in the labels file
            if chanidx_is_explicit:  # but, if explicitly declared, use
                # that index number
                chanidx = int(curry_params.chanidx_in_file["CHAN_IN_FILE"
                              + CHANTYPES[key]][ind])
            if chanidx <= 0:   # if chanidx was explicitly declared to be ' 0',
                # it means the channel is not actually saved in the data file
                # (e.g. the "Ref" channel), so don't add it to our list.
                # Git issue #8391
                continue
            ch = {"ch_name": chan,
                  "unit": curry_params.unit_dict[key],
                  "kind": FIFFV_CHANTYPES[key],
                  "coil_type": FIFFV_COILTYPES[key],
                  "ch_idx": chanidx
                  }
            if key == "eeg":
                loc = np.array(sensors["SENSORS" + CHANTYPES[key]][ind], float)
                # XXX just the sensor, where is ref (next 3)?
                assert loc.shape == (3,)
                loc /= 1000.  # to meters
                loc = np.concatenate([loc, np.zeros(9)])
                ch['loc'] = loc
                # XXX need to check/ensure this
                ch['coord_frame'] = FIFF.FIFFV_COORD_HEAD
            elif key == 'meg':
                pos = np.array(sensors["SENSORS" + CHANTYPES[key]][ind], float)
                pos /= 1000.  # to meters
                pos = pos[:3]  # just the inner coil
                pos = apply_trans(curry_dev_dev_t, pos)
                nn = np.array(normals["NORMALS" + CHANTYPES[key]][ind], float)
                assert np.isclose(np.linalg.norm(nn), 1., atol=1e-4)
                nn /= np.linalg.norm(nn)
                nn = apply_trans(curry_dev_dev_t, nn, move=False)
                trans = np.eye(4)
                trans[:3, 3] = pos
                trans[:3, :3] = _normal_orth(nn).T
                ch['loc'] = _coil_trans_to_loc(trans)
                ch['coord_frame'] = FIFF.FIFFV_COORD_DEVICE
            all_chans.append(ch)

    ch_count = len(all_chans)
    assert (ch_count == curry_params.n_chans)  # ensure that we have assembled
    # the same number of channels as declared in the info (.DAP) file in the
    # DATA_PARAMETERS section. Git issue #8391

    # sort the channels to assure they are in the order that matches how
    # recorded in the datafile.  In general they most likely are already in
    # the correct order, but if the channel index in the data file was
    # explicitly declared we might as well use it.
    all_chans = sorted(all_chans, key=lambda ch: ch['ch_idx'])

    ch_names = [chan["ch_name"] for chan in all_chans]
    info = create_info(ch_names, curry_params.sfreq)
    info['meas_date'] = curry_params.dt_start          # for Git issue #8398
    _make_trans_dig(curry_paths, info, curry_dev_dev_t)

    for ind, ch_dict in enumerate(info["chs"]):
        all_chans[ind].pop('ch_idx')
        ch_dict.update(all_chans[ind])
        assert ch_dict['loc'].shape == (12,)
        ch_dict['unit'] = SI_UNITS[all_chans[ind]['unit'][1]]
        ch_dict['cal'] = SI_UNIT_SCALE[all_chans[ind]['unit'][0]]

    return info, curry_params.n_samples, curry_params.is_ascii