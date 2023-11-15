def _check_load_mat(fname, uint16_codec):
    """Check if the mat struct contains 'EEG'."""
    from ...externals.pymatreader import read_mat
    eeg = read_mat(fname, uint16_codec=uint16_codec)
    if 'ALLEEG' in eeg:
        raise NotImplementedError(
            'Loading an ALLEEG array is not supported. Please contact'
            'mne-python developers for more information.')
    if 'EEG' not in eeg:
        raise ValueError('Could not find EEG array in the .set file.')
    else:
        eeg = eeg['EEG']
    eeg = eeg.get('EEG', eeg)  # handle nested EEG structure
    eeg = Bunch(**eeg)
    eeg.trials = int(eeg.trials)
    eeg.nbchan = int(eeg.nbchan)
    eeg.pnts = int(eeg.pnts)
    return eeg