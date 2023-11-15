    def process_record(self, new, old=None):
        new = super(Account, self).process_record(new, old)

        # Store password safely in database as str
        # (bcrypt.hashpw returns base64 bytes).
        pwd_str = new["password"].encode(encoding='utf-8')
        hashed = bcrypt.hashpw(pwd_str, bcrypt.gensalt())
        new["password"] = hashed.decode(encoding='utf-8')

        # Administrators can reach other accounts and anonymous have no
        # selected_userid. So do not try to enforce.
        if self.context.is_administrator or self.context.is_anonymous:
            return new

        # Otherwise, we force the id to match the authenticated username.
        if new[self.model.id_field] != self.request.selected_userid:
            error_details = {
                'name': 'data.id',
                'description': 'Username and account ID do not match.',
            }
            raise_invalid(self.request, **error_details)

        return new