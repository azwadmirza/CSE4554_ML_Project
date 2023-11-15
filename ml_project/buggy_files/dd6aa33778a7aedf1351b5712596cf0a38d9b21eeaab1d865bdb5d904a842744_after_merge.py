    def __init__(self, csv_path, refresh_time=1):
        csv_filename = 'glances.csv'
        self.__refresh_time = refresh_time

        # Set the CSV output file
        csv_file = os.path.realpath(os.path.join(csv_path, csv_filename))

        try:
            if is_PY3:
                self.__csvfile_fd = open(csv_file, 'w', newline='')
            else:
                self.__csvfile_fd = open(csv_file, 'wb')
            self.__csvfile = csv.writer(self.__csvfile_fd)
        except IOError as error:
            print(_("Cannot create the CSV output file: %s") % error)
            sys.exit(2)