    def _get_goes_sat_num(start, end):
        """Parses the query time to determine which GOES satellite to use."""

        goes_operational = {
            2: TimeRange('1980-01-04', '1983-05-01'),
            5: TimeRange('1983-05-02', '1984-08-01'),
            6: TimeRange('1983-06-01', '1994-08-19'),
            7: TimeRange('1994-01-01', '1996-08-14'),
            8: TimeRange('1996-03-21', '2003-06-19'),
            9: TimeRange('1997-01-01', '1998-09-09'),
            10: TimeRange('1998-07-10', '2009-12-02'),
            11: TimeRange('2006-06-20', '2008-02-16'),
            12: TimeRange('2002-12-13', '2007-05-09'),
            13: TimeRange('2006-08-01', '2006-08-01'),
            14: TimeRange('2009-12-02', '2010-11-05'),
            15: TimeRange('2010-09-01', Time.now()),
        }

        sat_list = []
        for sat_num in goes_operational:
            if (goes_operational[sat_num].start <= start <= goes_operational[sat_num].end and
                    goes_operational[sat_num].start <= end <= goes_operational[sat_num].end):
                # if true then the satellite with sat_num is available
                sat_list.append(sat_num)

        if not sat_list:
            # if no satellites were found then raise an exception
            raise Exception('No operational GOES satellites within time range')
        else:
            return sat_list