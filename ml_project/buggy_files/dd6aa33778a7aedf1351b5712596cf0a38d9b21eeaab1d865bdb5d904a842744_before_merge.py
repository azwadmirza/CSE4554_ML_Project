    def __init__(self, cvsfile="./glances.csv", refresh_time=1):
        # Init refresh time
        self.__refresh_time = refresh_time

        # Set the ouput (CSV) path
        try:
            self.__cvsfile_fd = open("%s" % cvsfile, "wb")
            self.__csvfile = csv.writer(self.__cvsfile_fd)
        except IOError as error:
            print("Cannot create the output CSV file: ", error[1])
            sys.exit(0)