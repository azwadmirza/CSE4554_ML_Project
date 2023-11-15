def follow_through_dialog(browser, user_name, amount, dont_include, login, follow_restrict, allfollowing, is_random, delay, callbacks = []):
    followNum = 0
    sleep(2)
    person_followed = []

    if is_random:
        # expanding the popultaion for better sampling distribution
        amount = amount * 3

    # find dialog box
    dialog = browser.find_element_by_xpath("//div[text()='Followers' or text()='Following']/following-sibling::div")

    # scroll down the page
    scroll_bottom(browser, dialog, allfollowing)

    #Get follow buttons. This approch will find the follow buttons and ignore the Unfollow/Requested buttons.
    follow_buttons = dialog.find_elements_by_xpath("//div/div/span/button[text()='Follow']")

    person_list = []
    abort = False
    total_list = len(follow_buttons)

    while (total_list < amount) and not abort:
        amount_left = amount - total_list
        before_scroll = total_list
        scroll_bottom(browser, dialog, amount_left)
        sleep(1)
        follow_buttons = dialog.find_elements_by_xpath("//div/div/span/button[text()='Follow']")
        total_list = len(follow_buttons)
        abort = (before_scroll == total_list)

    for person in follow_buttons:

        if person and hasattr(person, 'text') and person.text:
            person_list.append(person.find_element_by_xpath("../../../*")
                               .find_elements_by_tag_name("a")[1].text)

    if amount >= total_list:
        amount = total_list
        print(user_name+" -> Less users to follow than requested.")

    # follow loop
    try:
        hasSlept = False
        btnPerson = list(zip(follow_buttons, person_list))
        if is_random:
            sample = random.sample(range(0, len(follow_buttons)), amount)
            finalBtnPerson = []
            for num in sample:
                finalBtnPerson.append(btnPerson[num])
        else:
            finalBtnPerson = btnPerson
        for button, person in finalBtnPerson:
            if followNum >= amount:
                print("--> Total followNum reached: ", followNum)
                break

            if followNum != 0 and hasSlept == False and followNum % 10 == 0:
                if delay < 60:
                    print('sleeping for about {} seconds'.format(delay))
                else:
                    print('sleeping for about {} minutes'.format(delay/60))
                sleep(delay)
                hasSlept = True
                continue

            if person not in dont_include:
                followNum += 1
                # Register this session's followed user for further interaction
                person_followed.append(person)

                button.send_keys("\n")
                log_followed_pool(login, person) 
                
                follow_restrict[user_name] = follow_restrict.get(user_name, 0) + 1

                print('--> Ongoing follow ' + str(followNum) + ', now following: {}'.format(
                    person.encode('utf-8')))
                for callback in callbacks:
                    callback(person.encode('utf-8'))
                sleep(15)
                # To only sleep once until there is the next follow
                if hasSlept: hasSlept = False

                continue

            else:
                if is_random:
                    repickedNum = -1
                    while repickedNum not in sample and repickedNum != -1:
                        repickedNum = random.randint(0, len(btnPerson))
                    sample.append(repickedNum)
                    finalBtnPerson.append(btnPerson[repickedNum])
                continue

    except BaseException as e:
        print("follow loop error \n", str(e))

    return person_followed