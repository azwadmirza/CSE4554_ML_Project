    def __init__(self, args):
        A = lambda x: args.__dict__[x] if x in args.__dict__ else None
        self.db_path = A('pan_or_profile_db') or A('profile_db') or A('pan_db')
        self.just_do_it = A('just_do_it')
        self.target_data_group_set_by_user = A('target_data_group') or None
        self.target_data_group = self.target_data_group_set_by_user or 'default'

        if not self.db_path:
            raise ConfigError("The AdditionalAndOrderDataBaseClass is inherited with an args object that did not\
                               contain any database path :/ Even though any of the following would\
                               have worked: `pan_or_profile_db`, `profile_db`, `pan_db` :(")

        if not self.table_name:
            raise ConfigError("The AdditionalAndOrderDataBaseClass does not know anything about the table it should\
                               be working with.")

        utils.is_pan_or_profile_db(self.db_path)
        self.db_type = utils.get_db_type(self.db_path)
        self.db_version = utils.get_required_version_for_db(self.db_path)

        database = db.DB(self.db_path, self.db_version)
        self.additional_data_keys = database.get_single_column_from_table(self.table_name, 'data_key')
        database.disconnect()

        Table.__init__(self, self.db_path, self.db_version, self.run, self.progress)

        self.nulls_per_type = {'str': '',
                               'int': 0,
                               'float': 0,
                               'stackedbar': None,
                               'unknown': None}