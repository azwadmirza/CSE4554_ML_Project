    def ask_vault_passwords(ask_vault_pass=False, ask_new_vault_pass=False, confirm_vault=False, confirm_new=False):
        ''' prompt for vault password and/or password change '''

        vault_pass = None
        new_vault_pass = None

        try:
            if ask_vault_pass:
                vault_pass = getpass.getpass(prompt="Vault password: ")

            if ask_vault_pass and confirm_vault:
                vault_pass2 = getpass.getpass(prompt="Confirm Vault password: ")
                if vault_pass != vault_pass2:
                    raise errors.AnsibleError("Passwords do not match")

            if ask_new_vault_pass:
                new_vault_pass = getpass.getpass(prompt="New Vault password: ")

            if ask_new_vault_pass and confirm_new:
                new_vault_pass2 = getpass.getpass(prompt="Confirm New Vault password: ")
                if new_vault_pass != new_vault_pass2:
                    raise errors.AnsibleError("Passwords do not match")
        except EOFError:
            pass

        # enforce no newline chars at the end of passwords
        if vault_pass:
            vault_pass = to_bytes(vault_pass, errors='strict', nonstring='simplerepr').strip()
        if new_vault_pass:
            new_vault_pass = to_bytes(new_vault_pass, errors='strict', nonstring='simplerepr').strip()

        return vault_pass, new_vault_pass