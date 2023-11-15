    def _set_keychain(self):
        """
        Lazy import to avoid conflict with pytest-xdist.
        """
        import objc
        from Foundation import NSBundle
        Security = NSBundle.bundleWithIdentifier_('com.apple.security')

        S_functions = [
            ('SecKeychainGetTypeID', b'I'),
            ('SecKeychainItemGetTypeID', b'I'),
            ('SecKeychainAddGenericPassword', b'i^{OpaqueSecKeychainRef=}I*I*I*o^^{OpaqueSecKeychainItemRef}'),
            ('SecKeychainOpen', b'i*o^^{OpaqueSecKeychainRef}'),
            ('SecKeychainFindGenericPassword', b'i@I*I*o^Io^^{OpaquePassBuff}o^^{OpaqueSecKeychainItemRef}'),
        ]

        objc.loadBundleFunctions(Security, globals(), S_functions)

        SecKeychainRef = objc.registerCFSignature('SecKeychainRef', b'^{OpaqueSecKeychainRef=}', SecKeychainGetTypeID())
        SecKeychainItemRef = objc.registerCFSignature('SecKeychainItemRef', b'^{OpaqueSecKeychainItemRef=}', SecKeychainItemGetTypeID())
        PassBuffRef = objc.createOpaquePointerType('PassBuffRef', b'^{OpaquePassBuff=}', None)

        # Get the login keychain
        result, login_keychain = SecKeychainOpen(b'login.keychain', None)
        self.login_keychain = login_keychain