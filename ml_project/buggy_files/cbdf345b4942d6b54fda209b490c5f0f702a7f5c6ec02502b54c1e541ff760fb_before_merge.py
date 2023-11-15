    def saveDataSet(self, event):
        """
        Saves the final dataframe
        """

        # Backup previous save
        from sys import platform

        csv_path = os.path.join(self.dir, "CollectedData_" + self.scorer + ".csv")
        hdf_path = os.path.join(self.dir, "CollectedData_" + self.scorer + ".h5")
        csv_backup_path = csv_path.replace(".csv", ".csv.backup")
        hdf_backup_path = hdf_path.replace(".h5", ".h5.backup")

        if platform == "linux" or platform == "linux2":
            if os.path.exists(csv_path):
                os.rename(csv_path, csv_backup_path)

            if os.path.exists(hdf_path):
                os.rename(hdf_path, hdf_backup_path)

        elif platform == "win32":
            if os.path.exists(csv_path):
                if os.path.exists(
                    csv_backup_path
                ):  # check if backupfile exists already
                    os.remove(
                        csv_backup_path
                    )  # requires double action as windows fails to rename file if exists already
                    os.rename(csv_path, csv_backup_path)

            if os.path.exists(hdf_path):
                if os.path.exists(hdf_backup_path):
                    os.remove(hdf_backup_path)
                    os.rename(hdf_path, hdf_backup_path)

        elif platform == "darwin":
            try:
                if os.path.exists(csv_path):
                    os.rename(csv_path, csv_backup_path)

                if os.path.exists(hdf_path):
                    os.rename(hdf_path, hdf_backup_path)
            except:
                print(" Unexpected os.rename behaviour, try win32 approach")

        self.statusbar.SetStatusText("File saved")
        MainFrame.saveEachImage(self)
        MainFrame.updateZoomPan(self)

        # Drop Nan data frames
        self.dataFrame = self.dataFrame.dropna(how="all")

        # Windows compatible
        self.dataFrame.sort_index(inplace=True)
        self.dataFrame = self.dataFrame.reindex(
            self.bodyparts,
            axis=1,
            level=self.dataFrame.columns.names.index("bodyparts"),
        )
        self.dataFrame.to_csv(csv_path)
        self.dataFrame.to_hdf(hdf_path, "df_with_missing", format="table", mode="w")