    def reload_from_db(self):
        """
        Read the timestamp from the database. If the timestamp is newer than
        the internal timestamp, then read the complete data
        :return:
        """
        if not self.timestamp or \
            self.timestamp + datetime.timedelta(seconds=current_app.config.get(
                "PI_CHECK_RELOAD_CONFIG", 0)) < datetime.datetime.now():
            db_ts = Config.query.filter_by(Key=PRIVACYIDEA_TIMESTAMP).first()
            if reload_db(self.timestamp, db_ts):
                self.config = {}
                self.resolver = {}
                self.realm = {}
                self.default_realm = None
                for sysconf in Config.query.all():
                    self.config[sysconf.Key] = {
                        "Value": sysconf.Value,
                        "Type": sysconf.Type,
                        "Description": sysconf.Description}
                for resolver in Resolver.query.all():
                    resolverdef = {"type": resolver.rtype,
                                   "resolvername": resolver.name}
                    data = {}
                    for rconf in resolver.config_list:
                        if rconf.Type == "password":
                            value = decryptPassword(rconf.Value)
                        else:
                            value = rconf.Value
                        data[rconf.Key] = value
                    resolverdef["data"] = data
                    self.resolver[resolver.name] = resolverdef

                for realm in Realm.query.all():
                    if realm.default:
                        self.default_realm = realm.name
                    realmdef = {"option": realm.option,
                                "default": realm.default,
                                "resolver": []}
                    for x in realm.resolver_list:
                        realmdef["resolver"].append({"priority": x.priority,
                                                     "name": x.resolver.name,
                                                     "type": x.resolver.rtype})
                    self.realm[realm.name] = realmdef

            self.timestamp = datetime.datetime.now()