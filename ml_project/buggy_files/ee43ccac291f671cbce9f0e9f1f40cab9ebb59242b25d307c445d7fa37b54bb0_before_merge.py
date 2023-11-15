  def add_functionary_key_from_gpg_keyid(self, gpg_keyid, gpg_home=None):
    """
    <Purpose>
      Load a functionary public key from the GPG keychain, located at the
      passed GPG home path, identified by the passed GPG keyid, and add it to
      the layout's dictionary of keys.

    <Arguments>
      gpg_keyid:
              A GPG keyid.

      gpg_home:
              A path to the GPG keychain to load the key from. If not passed
              the default GPG keychain is used.

    <Exceptions>
      securesystemslib.exceptions.FormatError
              If the passed gpg keyid does not match
              securesystemslib.formats.KEYID_SCHEMA.

              If the gpg home path is passed and does not match
              securesystemslib.formats.PATH_SCHEMA.

              If the key loaded from the GPG keychain does not match
              in_toto.formats.ANY_PUBKEY_SCHEMA.

    <Returns>
      The added functionary public key.

    """
    securesystemslib.formats.KEYID_SCHEMA.check_match(gpg_keyid)
    if gpg_home: # pragma: no branch
      securesystemslib.formats.PATH_SCHEMA.check_match(gpg_home)

    key = in_toto.gpg.functions.gpg_export_pubkey(gpg_keyid,
        homedir=gpg_home)
    return self.add_functionary_key(key)