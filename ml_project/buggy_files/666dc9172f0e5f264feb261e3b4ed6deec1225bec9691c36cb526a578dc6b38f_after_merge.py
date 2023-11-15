def get_given_user_followers(browser,
                             user_name,
                             amount,
                             dont_include,
                             login,
                             follow_restrict,
                             is_random):

    browser.get('https://www.instagram.com/' + user_name)

    # check how many poeple are following this user.
    # throw RuntimeWarning if we are 0 people following this user or
    # if its a private account
    try:
        allfollowing = formatNumber(
            browser.find_element_by_xpath("//li[2]/a/span").text)
    except NoSuchElementException:
        print ('Can\'t interact with private account')
        return

    following_link = browser.find_elements_by_xpath(
        '//a[@href="/' + user_name + '/followers/"]')
    following_link[0].send_keys("\n")

    sleep(2)

    # find dialog box
    dialog = browser.find_element_by_xpath(
        "//div[text()='Followers']/following-sibling::div")

    # scroll down the page
    scroll_bottom(browser, dialog, allfollowing)

    # get follow buttons. This approch will find the follow buttons and
    # ignore the Unfollow/Requested buttons.
    follow_buttons = dialog.find_elements_by_xpath(
        "//div/div/span/button[text()='Follow']")
    person_list = []

    if amount >= len(follow_buttons):
        amount = len(follow_buttons)
        print(user_name+" -> Less users to follow than requested.")

    finalBtnPerson = []
    if is_random:
        sample = random.sample(range(0, len(follow_buttons)), amount)

        for num in sample:
            finalBtnPerson.append(follow_buttons[num])
    else:
        finalBtnPerson = follow_buttons[0:amount]
    for person in finalBtnPerson:

        if person and hasattr(person, 'text') and person.text:
            person_list.append(person.find_element_by_xpath(
                "../../../*").find_elements_by_tag_name("a")[1].text)

    return person_list