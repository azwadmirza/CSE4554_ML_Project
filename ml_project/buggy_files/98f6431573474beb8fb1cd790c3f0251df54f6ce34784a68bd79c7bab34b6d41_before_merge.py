    def get_lock_filename(config) -> str:

        return str(config['user_data_dir'] / 'hyperopt.lock')