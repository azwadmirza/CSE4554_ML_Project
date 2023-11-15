def __query_and_simplify(searchTerm: str, apiKey: str = ytmApiKey) -> List[dict]:
    '''
    `str` `searchTerm` : the search term you would type into YTM's search bar

    RETURNS `list<dict>`

    For structure of dict, see comment at function declaration
    '''

    #! For dict structure, see end of this function (~ln 268, ln 283) and chill, this
    #! function ain't soo big, there are plenty of comments and blank lines



    # build and POST a query to YTM

    url = 'https://music.youtube.com/youtubei/v1/search?alt=json&key=' + apiKey

    headers = {
        'Referer': 'https://music.youtube.com/search'
    }

    payload = {

        'context': {
            'client': {
                'clientName': 'WEB_REMIX',
                'clientVersion': '0.1'
            }
        },

        'query': searchTerm
    }

    request = post(
        url     = url,
        headers = headers,
        json    = payload
    )

    response = convert_json_to_dict(request.text)

    #! We will hereon call generic levels of nesting as 'Blocks'. What follows is an
    #! overview of the basic nesting (you'll need it),
    #!
    #! Content blocks
    #!       Group results into 'Top result', 'Songs', 'Videos',
    #!       'playlists', 'Albums', 'User notices', etc...
    #!
    #! Result blocks (under each 'Content block')
    #!       Represents an individual song, album, video, ..., playlist
    #!       result
    #!
    #! Detail blocks (under each 'Result block')
    #!       Represents a detail of the result, these might be one of
    #!       name, duration, channel, album, etc...
    #!
    #! Link block (under each 'Result block')
    #!       Contains the video/Album/playlist/Song/Artist link of the
    #!       result as found on YouTube
    
    # Simplify and extract necessary details from senselessly nested YTM response
    #! This process is broken into numbered steps below

    #! nested-dict keys are used to (a) indicate nesting visually and (b) make the code
    #! more readable



    # 01. Break response into contentBLocks
    contentBlocks = response['contents'] \
        ['sectionListRenderer'] \
            ['contents']



    # 02. Gather all result block in the same place
    resultBlocks = []

    for cBlock in contentBlocks:
        # Ignore user-suggestion

        #! The 'itemSectionRenderer' field is for user notices (stuff like - 'showing
        #! results for xyz, search for abc instead') we have no use for them, the for
        #! loop below if throw a keyError if we don't ignore them
        if 'itemSectionRenderer' in cBlock.keys():
            continue

        for contents in cBlock['musicShelfRenderer']['contents']:
            #! apparently content Blocks without an 'overlay' field don't have linkBlocks
            #! I have no clue what they are and why there even exist
            if 'overlay' not in contents['musicResponsiveListItemRenderer']:
                continue

            result = contents['musicResponsiveListItemRenderer'] \
                ['flexColumns']
            


            # Add the linkBlock        
            
            linkBlock = contents['musicResponsiveListItemRenderer'] \
                ['overlay'] \
                    ['musicItemThumbnailOverlayRenderer'] \
                        ['content'] \
                            ['musicPlayButtonRenderer'] \
                                ['playNavigationEndpoint']
            
            #! detailsBlock is always a list, so we just append the linkBlock to it
            #! insted of carrying along all the other junk from 'musicResponsiveListItemRenderer'
            result.append(linkBlock)
        
            #! gather resultBlock
            resultBlocks.append(result)
    
    

    # 03. Gather available details in the same place

    #! We only need results that are Songs or Videos, so we filter out the rest, since
    #! Songs and Videos are supplied with different details, extracting all details from
    #! both is just carrying on redundant data, so we also have to selectively extract
    #! relevant details. What you need to know to understand how we do that here:
    #!
    #! Songs details are ALWAYS in the following order:
    #!       0 - Name
    #!       1 - Type (Song)
    #!       2 - Artist
    #!       3 - Album
    #!       4 - Duration (mm:ss)
    #!
    #! Video details are ALWAYS in the following order:
    #!       0 - Name
    #!       1 - Type (Video)
    #!       2 - Channel
    #!       3 - Viewers
    #!       4 - Duration (hh:mm:ss)
    #!
    #! We blindly gather all the details we get our hands on, then
    #! cherrypick the details we need based on  their index numbers,
    #! we do so only if their Type is 'Song' or 'Video

    simplifiedResults = []

    for result in resultBlocks:

        # Blindly gather available details
        availableDetails = []



        # Filterout dummies here itself
        #! 'musicResponsiveListItmeFlexColumnRenderer' should have more that one
        #! sub-block, if not its a dummy, why does the YTM response contain dummies?
        #! I have no clue. We skip these.
        
        #! Remember that we appended the linkBlock to result, treating that like the
        #! other constituents of a result block will lead to errors, hence the 'in
        #! result[:-1]'
        for detail in result[:-1]:
            if len(detail['musicResponsiveListItemFlexColumnRenderer']) < 2:
                continue
            
            #! if not a dummy, collect all available details
            availableDetails.append(
                detail['musicResponsiveListItemFlexColumnRenderer'] \
                    ['text'] \
                        ['runs'][0] \
                            ['text']
            )
        


        # Filterout non-Song/Video results and incomplete results here itself
        #! From what we know about detail order, note that [1] - indicate result type
        if availableDetails[1] in ['Song', 'Video'] and len(availableDetails) == 5:
            
            #! skip if result is in hours instead of minuts (no song is that long)
            if len(availableDetails[4].split(':')) != 2:
                    continue



            # grab position of result
            #! This helps for those oddball cases where 2+ results are rated equally,
            #! lower position --> better match
            resultPosition = resultBlocks.index(result)



            # grab result link
            #! this is nested as [playlistEndpoint/watchEndpoint][videoId/playlistId/...]
            #! so hardcoding the dict keys for data look up is an ardours process, since
            #! the sub-block pattern is fixed even though the key isn't, we just
            #! reference the dict keys by index
            endpointKey = list( result[-1].keys() )[1]
            resultIdKey = list( result[-1][endpointKey].keys() )[0]

            linkId = result[-1][endpointKey][resultIdKey]
            resultLink = 'https://www.youtube.com/watch?v=' + linkId



            # convert length into seconds
            minStr, secStr = availableDetails[4].split(':')

            #! handle leading zeroes (eg. 01, 09, etc...), they cause eval errors, there
            #! are a few oddball tracks that are only a few seconds long
            if minStr[0] == '0' and len(minStr) == 2:
                minStr = minStr[1]
            
            if secStr[0] == '0':
                secStr = secStr[1]
            
            time = eval(minStr)*60 + eval(secStr)



            # format relevant details
            if availableDetails[1] == 'Song':
            
                formattedDetails = {
                    'name'      : availableDetails[0],
                    'type'      : 'song',
                    'artist'    : availableDetails[2],
                    'album'     : availableDetails[3],
                    'length'    : time,
                    'link'      : resultLink,
                    'position'  : resultPosition
                }
            
                if formattedDetails not in simplifiedResults:
                    simplifiedResults.append(formattedDetails)
            
            elif availableDetails[1] == 'Video':
            
                formattedDetails = {
                    'name'      : availableDetails[0],
                    'type'      : 'video',
                    'length'    : time,
                    'link'      : resultLink,
                    'position'  : resultPosition
                }
            
                if formattedDetails not in simplifiedResults:
                    simplifiedResults.append(formattedDetails)
            
            #! Things like playlists, albums, etc... just get ignored
            


    # return the results
    return simplifiedResults