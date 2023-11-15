    def get_linecol(model_obj, as_dict=False):
        """ Gets the position of a model object in the sieve file.

        Args:
            model_obj: the model object
            as_dict: return the position as a dict instead of a tuple.

        Returns:
            Returns the line and column number for the model object's position in the sieve file.
            Default return type is a tuple of (line,col). Optionally, returns a dict when as_dict == True.

        """
        metamodel = textx.model.metamodel(model_obj)
        tup = metamodel.parser.pos_to_linecol(model_obj._tx_position)
        if as_dict:
            return dict(zip(['line', 'col'], tup))
        return tup