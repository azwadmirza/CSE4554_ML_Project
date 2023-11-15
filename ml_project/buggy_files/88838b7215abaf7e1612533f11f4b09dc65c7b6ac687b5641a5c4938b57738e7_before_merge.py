def _read_regpol_file(reg_pol_path):
    '''
    helper function to read a reg policy file and return decoded data
    '''
    returndata = None
    if os.path.exists(reg_pol_path):
        with open(reg_pol_path, 'rb') as pol_file:
            returndata = pol_file.read()
        returndata = returndata.decode('utf-16-le')
    return returndata