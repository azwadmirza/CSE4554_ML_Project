    def api_retrieve(self, api_key=settings.STRIPE_SECRET_KEY):
        # OVERRIDING the parent version of this function
        # Cards must be manipulated through a customer or account.
        # TODO: When managed accounts are supported, this method needs to check if
        # either a customer or account is supplied to determine the correct object to use.
        customer = self.customer.api_retrieve(api_key=api_key)

        # If the customer is deleted, the sources attribute will be absent.
        # eg. {"id": "cus_XXXXXXXX", "deleted": True}
        if "sources" not in customer:
            # We fake a native stripe InvalidRequestError so that it's caught like an invalid ID error.
            raise InvalidRequestError("No such source: %s" % (self.stripe_id), "id")

        return customer.sources.retrieve(self.stripe_id, expand=self.expand_fields)