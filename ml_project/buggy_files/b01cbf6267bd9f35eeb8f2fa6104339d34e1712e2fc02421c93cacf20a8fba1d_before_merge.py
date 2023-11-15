    def step(self, action):
        """Call step on wrapped env.

        This method is necessary to suppress a deprecated warning
        thrown by gym.Wrapper.

        Args:
            action (np.ndarray): An action provided by the agent.

        Returns:
            np.ndarray: Agent's observation of the current environment
            float: Amount of reward returned after previous action
            bool: Whether the episode has ended, in which case further step()
                calls will return undefined results
            dict: Contains auxiliary diagnostic information (helpful for
                debugging, and sometimes learning)

        """
        observation, reward, done, info = self.env.step(action)
        # gym envs that are wrapped in TimeLimit wrapper modify
        # the done/termination signal to be true whenever a time
        # limit expiration occurs. The following statement sets
        # the done signal to be True only if caused by an
        # environment termination, and not a time limit
        # termination. The time limit termination signal
        # will be saved inside env_infos as
        # 'BulletEnv.TimeLimitTerminated'
        if 'TimeLimit.truncated' in info:
            info['BulletEnv.TimeLimitTerminated'] = done  # done = True always
            done = not info['TimeLimit.truncated']
        return observation, reward, done, info