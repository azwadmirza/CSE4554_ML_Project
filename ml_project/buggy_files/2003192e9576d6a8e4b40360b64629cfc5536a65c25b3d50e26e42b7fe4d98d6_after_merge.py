def load_1D_EDS_SEM_spectrum():
    """
    Load an EDS-SEM spectrum

    Notes
    -----
    - Sample: EDS-TM002 provided by BAM (www.webshop.bam.de)
    - SEM Microscope: Nvision40 Carl Zeiss
    - EDS Detector: X-max 80 from Oxford Instrument
    """
    from hyperspy.io import load
    file_path = os.sep.join([os.path.dirname(__file__), 'eds',
                             'example_signals', '1D_EDS_SEM_Spectrum.hspy'])
    return load(file_path)