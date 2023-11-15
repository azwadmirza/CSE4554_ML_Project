def load_1D_EDS_TEM_spectrum():
    """
    Load an EDS-TEM spectrum

    Notes
    -----
    - Sample: FePt bimetallic nanoparticles
    - SEM Microscope: Tecnai Osiris 200 kV D658 AnalyticalTwin
    - EDS Detector: Super-X 4 detectors Brucker
    """
    from hyperspy.io import load
    file_path = os.sep.join([os.path.dirname(__file__), 'eds',
                             'example_signals', '1D_EDS_TEM_Spectrum.hdf5'])
    return load(file_path)