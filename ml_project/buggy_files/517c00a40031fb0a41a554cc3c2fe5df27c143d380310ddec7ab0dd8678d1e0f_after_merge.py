def verify_layout_signatures(layout_metablock, keys_dict):
  """
  <Purpose>
    Iteratively verifies the signatures of a Metablock object containing
    a Layout object for every verification key in the passed keys dictionary.

    Requires at least one key to be passed and requires every passed key to
    find a valid signature.

  <Arguments>
    layout_metablock:
            A Metablock object containing a Layout whose signatures are
            verified.

    keys_dict:
            A dictionary of keys to verify the signatures conformant with
            securesystemslib.formats.VERIFICATION_KEY_DICT_SCHEMA.

  <Exceptions>
    securesystemslib.exceptions.FormatError
      if the passed key dict does not match VERIFICATION_KEY_DICT_SCHEMA.

    SignatureVerificationError
      if an empty verification key dictionary was passed, or
      if any of the passed verification keys fails to verify a signature.

    securesystemslib.gpg.exceptions.KeyExpirationError:
      if any of the passed verification keys is an expired gpg key

  """
  securesystemslib.formats.VERIFICATION_KEY_DICT_SCHEMA.check_match(keys_dict)

  # Fail if an empty verification key dictionary was passed
  if len(keys_dict) < 1:
    raise SignatureVerificationError("Layout signature verification"
        " requires at least one key.")

  # Fail if any of the passed keys can't verify a signature on the Layout
  for junk, verify_key in six.iteritems(keys_dict):
    layout_metablock.verify_signature(verify_key)