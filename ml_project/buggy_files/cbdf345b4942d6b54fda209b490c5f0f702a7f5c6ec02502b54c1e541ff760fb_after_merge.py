    def saveDataSet(self, event):
        """
        Saves the final dataframe
        """
        self.statusbar.SetStatusText("File saved")
        MainFrame.saveEachImage(self)
        MainFrame.updateZoomPan(self)

        # Windows compatible
        self.dataFrame.sort_index(inplace=True)
        self.dataFrame = self.dataFrame.reindex(
            self.bodyparts,
            axis=1,
            level=self.dataFrame.columns.names.index("bodyparts"),
        )
        self.dataFrame.to_csv(
            os.path.join(self.dir, "CollectedData_" + self.scorer + ".csv")
        )
        self.dataFrame.to_hdf(
            os.path.join(self.dir, "CollectedData_" + self.scorer + ".h5"),
            "df_with_missing",
            format="table",
            mode="w",
        )