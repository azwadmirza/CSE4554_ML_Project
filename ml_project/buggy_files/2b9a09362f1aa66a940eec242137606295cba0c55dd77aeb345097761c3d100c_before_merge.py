def _get_csr_extensions(csr):
    '''
    Returns a list of dicts containing the name, value and critical value of
    any extension contained in a csr object.
    '''
    ret = OrderedDict()

    csrtempfile = tempfile.NamedTemporaryFile()
    csrtempfile.write(csr.as_pem())
    csrtempfile.flush()
    csryaml = _parse_openssl_req(csrtempfile.name)
    csrtempfile.close()
    if csryaml and 'Requested Extensions' in csryaml['Certificate Request']['Data']:
        csrexts = csryaml['Certificate Request']['Data']['Requested Extensions']

        for short_name, long_name in six.iteritems(EXT_NAME_MAPPINGS):
            if long_name in csrexts:
                ret[short_name] = csrexts[long_name]

    return ret