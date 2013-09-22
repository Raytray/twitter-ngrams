from pymongo import MongoClient, ASCENDING
from collections import OrderedDict


client = MongoClient()
mongo_coll = client['twitter_ngrams']['tweets']
mongo_coll.ensure_index('text', ASCENDING)


def find(token=None):
    return_dict = {}
    text_token = "text.{}".format(token)
    if token:
        for item in mongo_coll.find({text_token: {'$exists': True}}):
            return_dict[item['_id']] = {'text': token,
                                       'percentage': (item['text'][token]/
                                                      float(sum(item['text'].values())))}
    else:
        for item in mongo_coll.find():
            return_dict[item['_id']] = {'text': sum(item['text'].values())}

    return OrderedDict(sorted(return_dict.items(), key=lambda t: t[0]))
