    def api_retrieve(self, api_key=settings.STRIPE_SECRET_KEY):
        # OVERRIDING the parent version of this function
        # Cards must be manipulated through a customer or account.
        # TODO: When managed accounts are supported, this method needs to check if either a customer or
        #       account is supplied to determine the correct object to use.

        return self.customer.api_retrieve(api_key=api_key).sources.retrieve(self.stripe_id, expand=self.expand_fields)