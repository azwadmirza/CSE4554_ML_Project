    def manage_DAVget(self):
        """Gets the document source or file data.

        This implementation is a last resort fallback. The subclass should
        override this method to provide a more appropriate implementation.

        Using PrincipiaSearchSource, if it exists. It is one of the few shared
        interfaces still around in common Zope content objects.
        """
        if getattr(aq_base(self), 'PrincipiaSearchSource', None) is not None:
            return self.PrincipiaSearchSource()

        # If it doesn't exist, give up.
        return ''