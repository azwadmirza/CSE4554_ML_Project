    def _add_player(self, player_id):
        """
        Add player to mpris_players
        """
        if not player_id.startswith(SERVICE_BUS):
            return False

        player = self._dbus.get(player_id, SERVICE_BUS_URL)

        if player.Identity not in self._mpris_names:
            self._mpris_names[player.Identity] = player_id.split(".")[-1]
            for p in self._mpris_players.values():
                if not p["name"] and p["identity"] in self._mpris_names:
                    p["name"] = self._mpris_names[p["identity"]]
                    p["full_name"] = u"{} {}".format(p["name"], p["index"])

        identity = player.Identity
        name = self._mpris_names.get(identity)
        if (
            self.player_priority != []
            and name not in self.player_priority
            and "*" not in self.player_priority
        ):
            return False

        if identity not in self._mpris_name_index:
            self._mpris_name_index[identity] = 0

        status = player.PlaybackStatus
        state_priority = WORKING_STATES.index(status)
        index = self._mpris_name_index[identity]
        self._mpris_name_index[identity] += 1
        try:
            subscription = player.PropertiesChanged.connect(
                self._player_monitor(player_id)
            )
        except AttributeError:
            subscription = {}

        self._mpris_players[player_id] = {
            "_dbus_player": player,
            "_id": player_id,
            "_state_priority": state_priority,
            "index": index,
            "identity": identity,
            "name": name,
            "full_name": u"{} {}".format(name, index),
            "status": status,
            "subscription": subscription,
        }

        return True