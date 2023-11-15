def _init_libcrypto():
    '''
    Set up libcrypto argtypes and initialize the library
    '''
    libcrypto = _load_libcrypto()

    libcrypto.RSA_new.argtypes = ()
    libcrypto.RSA_new.restype = c_void_p
    libcrypto.RSA_free.argtypes = (c_void_p, )
    libcrypto.RSA_size.argtype = (c_void_p)
    libcrypto.BIO_new_mem_buf.argtypes = (c_char_p, c_int)
    libcrypto.BIO_new_mem_buf.restype = c_void_p
    libcrypto.BIO_free.argtypes = (c_void_p, )
    libcrypto.PEM_read_bio_RSAPrivateKey.argtypes = (c_void_p, c_void_p, c_void_p, c_void_p)
    libcrypto.PEM_read_bio_RSAPrivateKey.restype = c_void_p
    libcrypto.PEM_read_bio_RSA_PUBKEY.argtypes = (c_void_p, c_void_p, c_void_p, c_void_p)
    libcrypto.PEM_read_bio_RSA_PUBKEY.restype = c_void_p
    libcrypto.RSA_private_encrypt.argtypes = (c_int, c_char_p, c_char_p, c_void_p, c_int)
    libcrypto.RSA_public_decrypt.argtypes = (c_int, c_char_p, c_char_p, c_void_p, c_int)

    try:
        libcrypto.OPENSSL_init_crypto()
    except AttributeError:
        # Support for OpenSSL < 1.1 (OPENSSL_API_COMPAT < 0x10100000L)
        libcrypto.OPENSSL_no_config()
        libcrypto.OPENSSL_add_all_algorithms_noconf()

    return libcrypto