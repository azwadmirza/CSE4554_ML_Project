  def sign_gpg(self, gpg_keyid=None, gpg_home=None):
    """
    <Purpose>
      Signs the utf-8 encoded canonical JSON bytes of the Link or Layout object
      contained in `self.signed` using `gpg.functions.create_signature` and
      appends the created signature to `self.signatures`.

    <Arguments>
      gpg_keyid: (optional)
              A gpg keyid, if omitted the default signing key is used

      gpg_home: (optional)
              The path to the gpg keyring, if omitted the default gpg keyring
              is used

    <Exceptions>
      securesystemslib.gpg.exceptions.CommandError:
              If the gpg signing command returned a non-zero exit code, e.g.
              because the key has expired.


    <Returns>
      The dictionary representation of the newly created signature.

    """
    signature = securesystemslib.gpg.functions.create_signature(
        self.signed.signable_bytes, gpg_keyid, gpg_home)

    self.signatures.append(signature)

    return signature