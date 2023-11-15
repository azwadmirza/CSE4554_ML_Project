    def x_to_index(self, x) -> pd.DataFrame:
        """
        Decode dataframe index from x.

        Returns:
            dataframe with time index column for first prediction and group ids
        """
        index_data = {self.time_idx: x["decoder_time_idx"][:, 0]}
        for id in self.group_ids:
            index_data[id] = x["groups"][:, self.group_ids.index(id)]
            # decode if possible
            index_data[id] = self.transform_values(id, index_data[id], inverse=True)
        index = pd.DataFrame(index_data)
        return index