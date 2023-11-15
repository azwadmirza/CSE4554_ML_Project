    def saveDataSet(self, event):
        """
        Saves the final dataframe
        """
        self.statusbar.SetStatusText("File saved")
        MainFrame.saveEachImage(self)
        MainFrame.updateZoomPan(self)

        # Windows compatible
        self.dataFrame.sort_index(inplace=True)
        # Discard data associated with bodyparts that are no longer in the config
        config_bpts = self.cfg["multianimalbodyparts"] + self.cfg["uniquebodyparts"]
        valid = [
            bp in config_bpts
            for bp in self.dataFrame.columns.get_level_values("bodyparts")
        ]
        self.dataFrame = self.dataFrame.loc[:, valid]
        # Re-organize the dataframe so the CSV looks consistent with the config
        self.dataFrame = self.dataFrame.reindex(
            columns=self.individual_names, level="individuals"
        ).reindex(columns=config_bpts, level="bodyparts")
        self.dataFrame.to_csv(
            os.path.join(self.dir, "CollectedData_" + self.scorer + ".csv")
        )
        self.dataFrame.to_hdf(
            os.path.join(self.dir, "CollectedData_" + self.scorer + ".h5"),
            "df_with_missing",
            format="table",
            mode="w",
        )