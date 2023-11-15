def getFeed(urls):
    feedPosts = []
    with FuturesSession() as session:
        futures = [session.get('{instance}{user}'.format(instance=NITTERINSTANCE, user=u.username)) for u in urls]
        for future in as_completed(futures):
            res = future.result().content.decode('utf-8')
            html = BeautifulSoup(res, "html.parser")
            userFeed = html.find_all('div', attrs={'class':'timeline-item'})
            if userFeed != []:
                    for post in userFeed[:-1]:
                        date_time_str = post.find('span', attrs={'class':'tweet-date'}).find('a')['title'].replace(",","")
                        time = datetime.datetime.now() - datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                        if time.days >=7:
                            continue

                        if post.find('div', attrs={'class':'pinned'}):
                            if post.find('div', attrs={'class':'pinned'}).find('span', attrs={'icon-pin'}):
                                continue

                        newPost = twitterPost()
                        newPost.op = post.find('a', attrs={'class':'username'}).text
                        newPost.twitterName = post.find('a', attrs={'class':'fullname'}).text
                        newPost.timeStamp = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
                        newPost.date = post.find('span', attrs={'class':'tweet-date'}).find('a').text
                        newPost.content = Markup(post.find('div',  attrs={'class':'tweet-content'}))
                        
                        if post.find('div', attrs={'class':'retweet-header'}):
                            newPost.username = post.find('div', attrs={'class':'retweet-header'}).find('div', attrs={'class':'icon-container'}).text
                            newPost.isRT = True
                        else:
                            newPost.username = newPost.op
                            newPost.isRT = False
                        
                        newPost.profilePic = NITTERINSTANCE+post.find('a', attrs={'class':'tweet-avatar'}).find('img')['src'][1:]
                        newPost.url = NITTERINSTANCE + post.find('a', attrs={'class':'tweet-link'})['href'][1:]
                        if post.find('div', attrs={'class':'quote'}):
                            newPost.isReply = True
                            quote = post.find('div', attrs={'class':'quote'})
                            if quote.find('div',  attrs={'class':'quote-text'}):
                                newPost.replyingTweetContent = Markup(quote.find('div',  attrs={'class':'quote-text'}))
                                
                            if quote.find('a', attrs={'class':'still-image'}):
                                newPost.replyAttachedImg = NITTERINSTANCE+quote.find('a', attrs={'class':'still-image'})['href'][1:]
                            
                            if quote.find('div', attrs={'class':'unavailable-quote'}):
                                newPost.replyingUser="Unavailable"
                            else:
                                newPost.replyingUser=quote.find('a',  attrs={'class':'username'}).text
                            post.find('div', attrs={'class':'quote'}).decompose()

                        if post.find('div',  attrs={'class':'attachments'}):
                            if not post.find(class_='quote'):
                                if  post.find('div',  attrs={'class':'attachments'}).find('a', attrs={'class':'still-image'}):
                                    newPost.attachedImg = NITTERINSTANCE + post.find('div',  attrs={'class':'attachments'}).find('a')['href'][1:]
                        feedPosts.append(newPost)
    return feedPosts