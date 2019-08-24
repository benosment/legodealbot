#! /usr/bin/env python3

import praw
import re

query_terms = ['assembly square', 'treehouse', 'modular']


def search_post(submission):
    found_list = []
    for query in query_terms:
        pattern = re.compile(query)
        match = pattern.search(submission.title.lower())
        if match:
            found_list.append(match.group(0))
        match = pattern.search(submission.selftext.lower())
        if match:
            found_list.append(match.group(0))
    return set(found_list)


if __name__ == '__main__':
    reddit = praw.Reddit('legodealbot')
    subreddit = reddit.subreddit('legodeal')

    for submission in subreddit.stream.submissions():
        print('Searching post: %s' % submission.title)
        found = search_post(submission)
        if found:
            print('Found %s' % ','.join(found))
