def bcf_hyperspectra(obj_bcf, index=None, downsample=None, cutoff_at_kV=None,  # noqa
                     lazy=False):
    """ Return hyperspy required list of dict with eds
    hyperspectra and metadata.
    """
    global warn_once
    if (fast_unbcf == False) and warn_once:
        _logger.warning("""unbcf_fast library is not present...
Parsing BCF with Python-only backend, which is slow... please wait.
If parsing is uncomfortably slow, first install cython, then reinstall hyperspy.
For more information, check the 'Installing HyperSpy' section in the documentation.""")
        warn_once = False
    if index is None:
        indexes = [obj_bcf.def_index]
    elif index == 'all':
        indexes = obj_bcf.available_indexes
    else:
        indexes = [obj_bcf.check_index_valid(index)]
    hyperspectra = []
    mode = obj_bcf.header.mode
    mapping = get_mapping(mode)
    for index in indexes:
        obj_bcf.persistent_parse_hypermap(index=index, downsample=downsample,
                                      cutoff_at_kV=cutoff_at_kV, lazy=lazy)
        eds_metadata = obj_bcf.header.get_spectra_metadata(index=index)
        hyperspectra.append({'data': obj_bcf.hypermap[index].hypermap,
                     'axes': [{'name': 'height',
                               'size': obj_bcf.hypermap[index].hypermap.shape[0],
                               'offset': 0,
                               'scale': obj_bcf.hypermap[index].ycalib,
                               'units': obj_bcf.header.units},
                              {'name': 'width',
                               'size': obj_bcf.hypermap[index].hypermap.shape[1],
                               'offset': 0,
                               'scale': obj_bcf.hypermap[index].xcalib,
                               'units': obj_bcf.header.units},
                              {'name': 'Energy',
                               'size': obj_bcf.hypermap[index].hypermap.shape[2],
                               'offset': obj_bcf.hypermap[index].calib_abs,
                               'scale': obj_bcf.hypermap[index].calib_lin,
                               'units': 'keV'}],
                     'metadata':
                     # where is no way to determine what kind of instrument was used:
                     # TEM or SEM
                     {'Acquisition_instrument': {
                         mode: obj_bcf.header.get_acq_instrument_dict(
                             detector=True,
                             index=index)
                     },
        'General': {'original_filename': obj_bcf.filename.split('/')[-1],
                         'title': 'EDX',
                         'date': obj_bcf.header.date,
                         'time': obj_bcf.header.time},
        'Sample': {'name': obj_bcf.header.name,
                         'elements': sorted(list(obj_bcf.header.elements)),
                         'xray_lines': sorted(gen_elem_list(obj_bcf.header.elements))},
        'Signal': {'signal_type': 'EDS_%s' % mode,
                         'record_by': 'spectrum',
                         'quantity': 'X-rays (Counts)'}
    },
        'original_metadata': {'Hardware': eds_metadata.hardware_metadata,
                              'Detector': eds_metadata.detector_metadata,
                              'Analysis': eds_metadata.esma_metadata,
                              'Spectrum': eds_metadata.spectrum_metadata,
                              'DSP Configuration': obj_bcf.header.dsp_metadata,
                              'Line counter': obj_bcf.header.line_counter,
                              'Stage': obj_bcf.header.stage_metadata,
                              'Microscope': obj_bcf.header.sem_metadata},
        'mapping': mapping,
    })
    return hyperspectra