    def perform_action(self, user, technique, target=None):
        """ Do something with the thing: animated

        :param user:
        :param technique: Not a dict: a Technique or Item
        :param target:

        :returns:
        """
        technique.advance_round()

        result = technique.use(user, target)

        try:
            tools.load_sound(technique.sfx).play()
        except AttributeError:
            pass

        # action is performed, so now use sprites to animate it
        # this value will be None if the target is off screen
        target_sprite = self._monster_sprite_map.get(target, None)

        # slightly delay the monster shake, so technique animation
        # is synchronized with the damage shake motion
        hit_delay = 0
        if user:
            message = trans('combat_used_x', {"user": user.name, "name": technique.name})

            # TODO: a real check or some params to test if should tackle, etc
            if technique in user.moves:
                hit_delay += .5
                user_sprite = self._monster_sprite_map[user]
                self.animate_sprite_tackle(user_sprite)

                if target_sprite:
                    self.task(partial(self.animate_sprite_take_damage, target_sprite), hit_delay + .2)
                    self.task(partial(self.blink, target_sprite), hit_delay + .6)

                # Track damage
                self._damage_map[target].add(user)

            else:  # assume this was an item used
                if result:
                    message += "\n" + trans('item_success')
                else:
                    message += "\n" + trans('item_failure')

            self.alert(message)
            self.suppress_phase_change()

        else:
            if result:
                self.suppress_phase_change()
                self.alert(trans('combat_status_damage', {"name": target.name, "status": technique.name}))

        if result and target_sprite and hasattr(technique, "images"):
            tech_sprite = self.get_technique_animation(technique)
            tech_sprite.rect.center = target_sprite.rect.center
            self.task(tech_sprite.image.play, hit_delay)
            self.task(partial(self.sprites.add, tech_sprite, layer=50), hit_delay)
            self.task(tech_sprite.kill, 3)