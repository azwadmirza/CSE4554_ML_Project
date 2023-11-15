def _download_data_arff(file_id, sparse, data_home, encode_nominal=True):
    # Accesses an ARFF file on the OpenML server. Documentation:
    # https://www.openml.org/api_data_docs#!/data/get_download_id
    # encode_nominal argument is to ensure unit testing, do not alter in
    # production!
    url = _DATA_FILE.format(file_id)
    response = _open_openml_url(url, data_home)
    if sparse is True:
        return_type = _arff.COO
    else:
        return_type = _arff.DENSE

    if PY2:
        arff_file = _arff.load(response.read(), encode_nominal=encode_nominal,
                               return_type=return_type, )
    else:
        arff_file = _arff.loads(response.read().decode('utf-8'),
                                encode_nominal=encode_nominal,
                                return_type=return_type)
    response.close()
    return arff_file