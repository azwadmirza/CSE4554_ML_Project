        def more_todo():
            """
            Check if there are any more minions we are waiting on returns from
            """
            return any(x is False for x in minions.values())