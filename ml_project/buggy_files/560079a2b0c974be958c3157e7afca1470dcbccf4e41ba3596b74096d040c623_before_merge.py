    def _get_replica_stats(self, db, is_mariadb, replication_channel):
        replica_results = {}
        try:
            with closing(db.cursor(pymysql.cursors.DictCursor)) as cursor:
                if is_mariadb and replication_channel:
                    cursor.execute("SET @@default_master_connection = '{0}';".format(replication_channel))
                    cursor.execute("SHOW SLAVE STATUS;")
                elif replication_channel:
                    cursor.execute("SHOW SLAVE STATUS FOR CHANNEL '{0}';".format(replication_channel))
                else:
                    cursor.execute("SHOW SLAVE STATUS;")

                if replication_channel:
                    slave_results = cursor.fetchone()
                else:
                    slave_results = cursor.fetchall()

                if slave_results:
                    if replication_channel:
                        replica_results.update(slave_results)
                    elif len(slave_results) > 0:
                        for slave_result in slave_results:
                            # MySQL <5.7 does not have Channel_Name.
                            # For MySQL >=5.7 'Channel_Name' is set to an empty string by default
                            channel = slave_result.get('Channel_Name') or 'default'
                            for key in slave_result:
                                if slave_result[key] is not None:
                                    if key not in replica_results:
                                        replica_results[key] = {}
                                    replica_results[key]["channel:{0}".format(channel)] = slave_result[key]
        except (pymysql.err.InternalError, pymysql.err.OperationalError) as e:
            errno, msg = e.args
            if errno == 1617 and msg == "There is no master connection '{0}'".format(replication_channel):
                # MariaDB complains when you try to get slave status with a
                # connection name on the master, without connection name it
                # responds an empty string as expected.
                # Mysql behaves the same with or without connection name.
                pass
            else:
                self.warning("Privileges error getting replication status (must grant REPLICATION CLIENT): %s" % str(e))

        try:
            with closing(db.cursor(pymysql.cursors.DictCursor)) as cursor:
                cursor.execute("SHOW MASTER STATUS;")
                binlog_results = cursor.fetchone()
                if binlog_results:
                    replica_results.update({'Binlog_enabled': True})
        except (pymysql.err.InternalError, pymysql.err.OperationalError) as e:
            self.warning("Privileges error getting binlog information (must grant REPLICATION CLIENT): %s" % str(e))

        return replica_results