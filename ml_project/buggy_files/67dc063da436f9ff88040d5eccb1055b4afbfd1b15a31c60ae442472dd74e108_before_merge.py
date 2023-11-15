    def cmd_get_state(self):
        """Get pickled state for restarting qtile"""
        buf = io.BytesIO()
        pickle.dump(QtileState(self), buf, protocol=0)
        state = buf.getvalue().decode()
        logger.debug('State = ')
        logger.debug(''.join(state.split('\n')))
        return state