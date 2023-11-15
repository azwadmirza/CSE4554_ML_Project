    def add(self, value):
        if normalize_index.flatten:
            if type(value) is tuple:
                _value = flatten_tuple(value)
                _d = len(_value)
                if _d == 1:
                    _value = _value[0]
            else:
                _value = value
                _d = 1
        else:
            # If we are not normalizing indices, then we cannot reliably
            # infer the set dimen
            _value = value
            _d = None

        if _value not in self._domain:
            raise ValueError("Cannot add value %s to Set %s.\n"
                             "\tThe value is not in the domain %s"
                             % (value, self.name, self._domain))

        # We wrap this check in a try-except because some values (like lists)
        #  are not hashable and can raise exceptions.
        try:
            if _value in self:
                logger.warning(
                    "Element %s already exists in Set %s; no action taken"
                    % (value, self.name))
                return False
        except:
            exc = sys.exc_info()
            raise TypeError("Unable to insert '%s' into Set %s:\n\t%s: %s"
                            % (value, self.name, exc[0].__name__, exc[1]))

        if self._filter is not None:
            if not self._filter(self, _value):
                return False

        if self._validate is not None:
            try:
                flag = self._validate(self, _value)
            except:
                logger.error(
                    "Exception raised while validating element '%s' for Set %s"
                    % (value, self.name))
                raise
            if not flag:
                raise ValueError(
                    "The value=%s violates the validation rule of Set %s"
                    % (value, self.name))

        # If the Set has a fixed dimension, check that this element is
        # compatible.
        if self._dimen is not None:
            if _d != self._dimen:
                if self._dimen is _UnknownSetDimen:
                    # The first thing added to a Set with unknown
                    # dimension sets its dimension
                    self._dimen = _d
                else:
                    raise ValueError(
                        "The value=%s has dimension %s and is not valid for "
                        "Set %s which has dimen=%s"
                        % (value, _d, self.name, self._dimen))

        # Add the value to this object (this last redirection allows
        # derived classes to implement a different storage mmechanism)
        self._add_impl(_value)
        return True