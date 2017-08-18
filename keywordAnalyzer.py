# This bot analyzes new comments made all over reddit with keywords provided.
# It then takes the entire string (comment) with the keyword and keeps returning
# it and stores it in a file. 
# Author: Mohammad Zariff Ahsham Ali
# License: MIT License

import praw
import re
import time
import json
import os

historyPath = '/home/zariff/Python Projects/Reddit Bot/commented.txt'

def authenticate():
    # Uses PRAW to set up a reddit instance with credentials
    # in praw.ini located in the project directory

    print 'Authenticating...'
    try:
        redditInstance = praw.Reddit('keywordAnalyzer', user_agent = 'keywordAnalyzer-bot: v 1.0 (dev: /u/zarifff)')
        print 'Successfully Authenticated! Current user: {}\n'.format(redditInstance.user.me())
        return redditInstance
    except:
        print 'Error! Could not Authenticate. Please check credentials.'
        pass

def chooseRunType():
    # Allows user to choose one of three options
    # returns opton, keywordList, subredditList, quantity, submissionURL regardless of choice
    
    keywordList = []
    subredditList = ''
    quantity = 0
    submissionURL = ''
    option = int(raw_input('Enter an option for the bot: \n\t1. Analyze all comments in a Reddit Submission Thread: \n\t2. Analyze comments from specified submissions in desired subreddit(s)\n\t3. Analyze all recent comments in a subreddit\n\tOption >>> '))

    if(option == 1):
        submissionURL = raw_input('Enter URL of submission: ')
        keywordList = keywordsToSearch()

    elif(option == 2):
        subredditList = raw_input('Enter subreddits to crawl. Use + only between multiple subreddits if required. Case sensitive (eg. leagueoflegends+DotA2): ')
        quantity = int(raw_input('Enter number of submissions to analyze. Will start from top: '))
        keywordList = keywordsToSearch()
    
    elif(option == 3):
        subredditList = raw_input('Enter subreddits to crawl. Use + only between multiple subreddits if required. Case sensitive (eg. leagueoflegends+DotA2): ')
        keywordList = keywordsToSearch()

    else:
        print 'invalid option. Exiting...'
        pass

    return option, keywordList, subredditList, quantity, submissionURL

def keywordsToSearch():
    # Asks the current user to input keywords to search for
    # Returns keywords as a list.
    keywordList = []
    keywordString = ''
    
    choice = raw_input('Press \'y\' to add keywords. Any other key to finish: ')
    if(choice.lower() == 'y'):
        keywordString = raw_input('Enter Keywords to search for (space-separated): ')
        keywordList = keywordString.split()

    return keywordList

def duplicateComment(commentID):
    # Checks a text file for duplicate comment IDs
    # If unique, appends current comment ID to file.

    duplicateCommentCheckFileRead = open(historyPath, 'r')
            
    if(commentID not in duplicateCommentCheckFileRead.read().splitlines()):
        duplicateCommentCheckFileRead.close()

        duplicateCommentCheckFileWrite = open(historyPath, 'a+')
        duplicateCommentCheckFileWrite.write(commentID + '\n')
        duplicateCommentCheckFileWrite.close()
        return False
    else:
        return True

def makeDict(comment):
    # to make json object and dump it
    return {str(comment.id) : {'body' : comment.body, 'created_utc' : comment.created_utc, 'ups' : comment.ups, 'downs' : comment.downs, 'score' : comment.score, 'subreddit' : comment.subreddit.display_name}}

def getCommentWithKeyWords(submission, keywordList):
    d = {}
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        keywordsToMatch = re.findall(r"(?=("+'|'.join(keywordList)+r"))", comment.body, re.IGNORECASE)
        if(keywordsToMatch and not duplicateComment(comment.id)):
            d.update(makeDict(comment))
    return d


def getcommentWithOutKeyWords(submission):
    d = {}
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        if(not duplicateComment(comment.id)):
            d.update(makeDict(comment))
    return d


def runKeywordAnalyzerBot(redditInstance, option, keywordList, subredditList, quantity, submissionURL, fileName):
    # Runs the bot. Depending on option number and parameters
    # currently uses print statements. Will modify later to analyze comments.
    d = {}
    data = {}

    if(option == 1):
        # Checks if URL is a valid reddit thread.
        try:
            submission = redditInstance.submission(url=submissionURL)
        except:
            print 'Invalid URL. Exiting...'
        
        # If no keywords were entered, 2nd case is performed.
        # Extracts all comments in the following order -> All top-level comments, all 2nd level comments...all n-level comments
        if(len(keywordList) > 0):
            d.update(getCommentWithKeyWords(submission, keywordList))
        else:
            d.update(getcommentWithOutKeyWords(submission))

        time.sleep(5)

    elif(option == 2):
        # Checks the current (quantity) hot submissions in the specified subreddits.
        # If keywords not specified, prints out all the comments from said subreddits according to quantity of submissions
        try:
            for submission in redditInstance.subreddit(subredditList).hot(limit=int(quantity)):
                print '\n\tSubreddit: {}\tSubmission Thread: {}'.format(submission.subreddit.display_name, submission.title)
                if(len(keywordList) > 0):
                    d.update(getCommentWithKeyWords(submission, keywordList))
                else:
                    d.update(getcommentWithOutKeyWords(submission))
                
                time.sleep(5)
        except:
            print 'Invalid subreddit names. Exiting...'
            pass

    elif(option == 3):
        # if using subreddit().stream.comments(), will print recent as well as future comments indefinitely
        # If using subreddit().comments(), will print out 'limit' number of comments at each iteration
        try:
            #for comment in redditInstance.subreddit(subredditList).stream.comments():
            for comment in redditInstance.subreddit(subredditList).comments(limit=25):
                if(len(keywordList) > 0):
                    keywordsToMatch = re.findall(r"(?=("+'|'.join(keywordList)+r"))", comment.body, re.IGNORECASE)
                    if(keywordsToMatch and not duplicateComment(comment.id)):
                        d.update(makeDict(comment))
                else:
                    d.update(makeDict(comment))
                
                time.sleep(1)
        except:
            print 'Invalid Subreddit List. Exiting...'
            pass
           
    else:
        'Invaild Option. Exiting...'
        pass        
    
    if(os.stat(fileName).st_size > 0):
        with open(fileName) as f:
            data = json.load(f)
            
    data.update(d)

    with open(fileName, 'w') as f:
        json.dump(data, f)

    print 'waiting 10 seconds...\n'
    time.sleep(10)

def main():
    redditInstance = authenticate()
    option, keywordList, subredditList, quantity, submissionURL = chooseRunType()
    fileName = raw_input('\nEnter Name of json file to dump data: ')
    fileName = '/home/zariff/Python Projects/Reddit Bot/' + fileName
    jsonFile = open(fileName, 'w')
    jsonFile.close()

    while True:
        runKeywordAnalyzerBot(redditInstance, option, keywordList, subredditList, quantity, submissionURL, fileName)


if __name__ == '__main__':
    main()
    
    
        
