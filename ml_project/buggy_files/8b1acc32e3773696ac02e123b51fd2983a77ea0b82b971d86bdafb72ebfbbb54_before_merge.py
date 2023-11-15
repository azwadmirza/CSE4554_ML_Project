    def interact_user_followers(self, usernames, amount=10, random=False):

        userToInteract = []
        if not isinstance(usernames, list):
            usernames = [usernames]
        try:
            for user in usernames:
                userToInteract += get_given_user_followers(self.browser, user, amount, self.dont_include, self.username, self.follow_restrict, random)
        except (TypeError, RuntimeWarning) as err:
            if type(err) == RuntimeWarning:
                print(u'Warning: {} , stopping follow_users'.format(err))
                self.logFile.write('Warning: {} , stopping follow_users\n'.format(err))

                return self
            else:
                print('Sorry, an error occured: {}'.format(err))
                self.logFile.write('Sorry, an error occured: {}\n'.format(err))
                self.aborting = True

                return self

        print('--> Users: {}'.format(len(userToInteract)))
        print('')
        userToInteract = sample(userToInteract, int(ceil(self.user_interact_percentage*len(userToInteract)/100)))
        self.like_by_users(userToInteract, self.user_interact_amount, self.user_interact_random, self.user_interact_media)

        return self