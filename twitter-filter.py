import tweepy
import ConfigParser

from collections import defaultdict
from pymongo import MongoClient, ASCENDING
from tokenizer import tokenize


config = ConfigParser.ConfigParser()
config.read('apikey.cfg')

consumer_key = config.get('DEFAULT', 'CONSUMER_KEY')
consumer_secret = config.get('DEFAULT', 'CONSUMER_SECRET')

access_token_key = config.get('DEFAULT', 'ACCESS_TOKEN_KEY')
access_token_secret = config.get('DEFAULT', 'ACCESS_TOKEN_SECRET')

auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth1.set_access_token(access_token_key, access_token_secret)

setTerms = ['mhacks', 'twitter']

mongo = MongoClient()
mongo_db = mongo['twitter_ngrams']
mongo_coll = mongo_db['tweets']

bad_tokens = ['.', '$'] # TODO: Do this in regex in tokenizer


class StreamListener(tweepy.StreamListener):
    def on_status(self, tweet):
        try:
            if insert_tweet(tweet):
                print "inserting {}".format(tweet.text.encode('ascii', 'ignore'))

        except Exception, e:
            print e

    def on_error(self, status_code):
        print 'Error: ' + repr(status_code)
        return False


def token_counter(def_dict, tweet):
    for token in tokenize(tweet.text.encode('ascii', 'ignore')):
        if (token not in bad_tokens and # get rid of chars that kill mongo
            not token.startswith('http') and # get rid of urls
            not token.startswith('@') and # get rid of Replies
            not token.startswith('#') and # get rid of hashtags
            len(token) >= 2):
            def_dict[token] += 1

    temp_dict = {k:v for k,v in def_dict.iteritems()}

    temp_tweet = {'_id': tweet.created_at,
                  'text': temp_dict}

    return mongo_coll.save(temp_tweet)


def insert_tweet(tweet):
    already_exists = mongo_coll.find_one({'_id': tweet.created_at})

    if already_exists:
        temp_dict = defaultdict(int, already_exists['text'])

    else:
        temp_dict = defaultdict(int)

    return token_counter(temp_dict, tweet)


def main():
    l = StreamListener()
    streamer = tweepy.Stream(auth=auth1, listener=l)
    streamer.filter(track=setTerms)


if __name__ == "__main__":
    main()
