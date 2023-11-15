def main():
    """Add all available states to our scene manager (tools.Control)
    and start the game using the pygame interface.

    :rtype: None
    :returns: None

    """
    import pygame
    from .control import PygameControl

    prepare.init()
    control = PygameControl(prepare.ORIGINAL_CAPTION)
    control.auto_state_discovery()

    # background state is used to prevent other states from
    # being required to track dirty screen areas.  for example,
    # in the start state, there is a menu on a blank background,
    # since menus do not clean up dirty areas, the blank,
    # "Background state" will do that.  The alternative is creating
    # a system for states to clean up their dirty screen areas.
    control.push_state("BackgroundState")

    # basically the main menu
    control.push_state("StartState")

    # Show the splash screen if it is enabled in the game configuration
    if prepare.CONFIG.splash == "1":
        control.push_state("SplashState")
        control.push_state("FadeInTransition")

    # block of code useful for testing
    if 0:
        import random
        from core.components.event.actions.player import Player
        from core.components.technique import Technique

        # TODO: fix this player/player1 issue
        control.player1 = prepare.player1

        add_monster = partial(adapter("add_monster"))
        Player().add_monster(control, add_monster('Bigfin', 10))
        Player().add_monster(control, add_monster('Dollfin', 10))
        Player().add_monster(control, add_monster('Rockitten', 10))
        Player().add_monster(control, add_monster('Nut', 10))
        Player().add_monster(control, add_monster('Sumobug', 10))

        add_item = partial(adapter("add_item"))
        Player().add_item(control, add_item(u'Potion', 1))
        Player().add_item(control, add_item(u'Super Potion', 1))
        Player().add_item(control, add_item(u'Capture Device', 1))

        for monster in control.player1.monsters:
            monster.hp = 100
            monster.current_hp = 1
            # monster.current_hp = random.randint(1, 2)
            monster.apply_status(Technique("status_poison"))

        # control.push_state("MonsterMenuState")

        from core.components.event.actions.combat import Combat
        start_battle = partial(adapter("random_encounter"))
        Combat().random_encounter(control, start_battle(1))

    control.main()
    pygame.quit()