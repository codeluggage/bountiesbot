import os
import json
from datetime import datetime, timedelta
import tweepy
import requests

bounty_list_url = 'https://api.bounties.network/bounty/'
explorer_url = 'https://explorer.bounties.network/bounty/'
date_format = '%Y-%m-%dT%H:%M:%S.%f'


def twitter_auth(tweepy, env):
    TWITTER_API_KEY = env.get('TWITTER_API_KEY')
    TWITTER_API_SECRET_KEY = env.get('TWITTER_API_SECRET_KEY')
    TWITTER_ACCESS_TOKEN = env.get('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = env.get('TWITTER_ACCESS_TOKEN_SECRET')
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

    return tweepy.API(auth)


def get_latest_tweet(twitter_api):
    return twitter_api.user_timeline(id='bountiesbot', count=1)[0]


def get_latest_bounty_id(tweet):
    try:
        return int(tweet.entities['urls'][0]['display_url'].split('/')[-1])
    except Exception as ex: # TODO: Make more specific
        print('Hit exception in get_latest_bounty_id: {}'.format(ex))
        return None


# A valid bounty can't be too new, or its unfurling is not available yet.
# Only bounties older than 1 minute are selected
def get_bounties(requests, url, bounty_id):
    try:
        res = []
        bounties = requests.get(url=url, params={
            'platform__in': 'bounties-network',
            'bountyStage__in': 1, # active bounties
            'ordering': '-bounty_created' # newest bounties
        }).json()

        for bounty in bounties['results']:
            # Only choose active bounties:
            if bounty['bounty_id'] <= bounty_id:
                continue

            created = datetime.strptime(bounty['created'], date_format)
            cutoff_time = datetime.now() - timedelta(seconds=30)
            # Bounties after this are too new, stop looping:
            if created > cutoff_time:
                break

            res.append(bounty)

        return res
    except Exception as ex: # TODO: Make more specific
        print('Hit exception in get_bounty: {}'.format(ex))
        return None


def tweet_bounty(event, context):
    try:
        # Authenticate with environment variables:
        twitter_api = twitter_auth(tweepy, os.environ)

        # Get the latest relevant tweet and the bounty it refers to:
        latest_tweet = get_latest_tweet(twitter_api)
        latest_bounty_id = get_latest_bounty_id(latest_tweet)
        bounties = get_bounties(requests, bounty_list_url, latest_bounty_id)

        # Walk through the remaining bounties we have not yet tweeted:
        tweet_count = 0
        for bounty in bounties[::-1]:
            tweet_count += 1
            latest_bounty_id += 1
            stripped_title = bounty['title']
            if len(stripped_title) > 130:
                stripped_title = stripped_title[0:130] + '...'
            status_text = (
                '🐝  Bzzz! There\'s a new bounty available!  🐝\n\n{}\n\n{}{}'
            ).format(stripped_title, explorer_url, bounty['id'])
            print('Tweeting this: ')
            print(status_text)
            twitter_api.update_status(status=status_text)

        return {
            'statusCode': 200,
            'body': 'Tweeted {} new bounties'.format(tweet_count)
        }
    except Exception as ex:
        print('Hit exception in tweet_bounty: {}'.format(ex))
        return {
            'statusCode': 500,
            'body': 'Failed with {}'.format(ex)
        }
