  def add_functionary_keys_from_gpg_keyids(self, gpg_keyid_list,
      gpg_home=None):
    """
    <Purpose>
      Load functionary public keys from the GPG keychain, located at the
      passed GPG home path, identified by the passed GPG keyids, and add it to
      the layout's dictionary of keys.

    <Arguments>
      gpg_keyid_list:
              A list of GPG keyids.

      gpg_home:
              A path to the GPG keychain to load the keys from. If not passed
              the default GPG keychain is used.

    <Exceptions>
      securesystemslib.exceptions.FormatError
              If any of the passed gpg keyids does not match
              securesystemslib.formats.KEYID_SCHEMA.

              If gpg home is passed and does not match
              securesystemslib.formats.PATH_SCHEMA.

              If any of the keys loaded from the GPG keychain does not
              match in_toto.formats.ANY_PUBKEY_SCHEMA.

    <Returns>
      A dictionary of the added functionary public keys with the key's keyids
      as dictionary keys and the keys as values.

    """
    securesystemslib.formats.KEYIDS_SCHEMA.check_match(gpg_keyid_list)
    key_dict = {}
    for gpg_keyid in gpg_keyid_list:
      key = self.add_functionary_key_from_gpg_keyid(gpg_keyid, gpg_home)
      key_dict[key["keyid"]] = key

    return key_dict