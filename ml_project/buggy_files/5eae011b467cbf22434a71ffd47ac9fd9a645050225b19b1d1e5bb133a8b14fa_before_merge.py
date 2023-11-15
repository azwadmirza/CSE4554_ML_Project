    def __repr__(self):
        if self._source is None:
            return f"<Vis  ({str(self._intent)}) mark: {self._mark}, score: {self.score} >"
        filter_intents = None
        channels, additional_channels = [], []
        for clause in self._inferred_intent:

            if hasattr(clause, "value"):
                if clause.value != "":
                    filter_intents = clause
            if hasattr(clause, "attribute"):
                if clause.attribute != "":
                    if clause.aggregation != "" and clause.aggregation is not None:
                        attribute = clause._aggregation_name.upper() + "(" + clause.attribute + ")"
                    elif clause.bin_size > 0:
                        attribute = "BIN(" + clause.attribute + ")"
                    else:
                        attribute = clause.attribute
                    if clause.channel == "x":
                        channels.insert(0, [clause.channel, attribute])
                    elif clause.channel == "y":
                        channels.insert(1, [clause.channel, attribute])
                    elif clause.channel != "":
                        additional_channels.append([clause.channel, attribute])

        channels.extend(additional_channels)
        str_channels = ""
        for channel in channels:
            str_channels += channel[0] + ": " + channel[1] + ", "

        if filter_intents:
            return f"<Vis  ({str_channels[:-2]} -- [{filter_intents.attribute}{filter_intents.filter_op}{filter_intents.value}]) mark: {self._mark}, score: {self.score} >"
        else:
            return f"<Vis  ({str_channels[:-2]}) mark: {self._mark}, score: {self.score} >"