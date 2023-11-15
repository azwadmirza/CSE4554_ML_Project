    def upsert(self, tableName, valueDict, keyDict):
        """
        Update values, or if no updates done, insert values
        TODO: Make this return true/false on success/error

        :param tableName: table to update/insert
        :param valueDict: values in table to update/insert
        :param keyDict:  columns in table to update/insert
        """

        changesBefore = self.connection.total_changes

        genParams = lambda myDict: [x + " = ?" for x in myDict]

        query = "UPDATE [" + tableName + "] SET " + ", ".join(genParams(valueDict)) + " WHERE " + " AND ".join(
            genParams(keyDict))

        self.action(query, list(itervalues(valueDict)) + list(itervalues(keyDict)))

        if self.connection.total_changes == changesBefore:
            query = "INSERT INTO [" + tableName + "] (" + ", ".join(list(valueDict) + list(keyDict)) + ")" + \
                    " VALUES (" + ", ".join(["?"] * len(list(valueDict) + list(keyDict))) + ")"
            self.action(query, list(itervalues(valueDict)) + list(itervalues(keyDict)))