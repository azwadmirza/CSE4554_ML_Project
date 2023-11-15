    def getcapacitypercent(self):
        if not self.initok or self.bat_list == []:
            return []
        # Init the bsum (sum of percent) and bcpt (number of batteries)
        # and Loop over batteries (yes a computer could have more than 1 battery)
        bsum = 0
        for bcpt in range(len(self.get())):
            try:
                bsum = bsum + int(self.bat_list[bcpt].capacity)
            except ValueError:
                return []
        bcpt = bcpt + 1
        # Return the global percent
        return int(bsum / bcpt)