from pymongo import MongoClient, ASCENDING


client = MongoClient()
mongo_coll = client['twitter_ngrams']['tweets']
mongo_coll.ensure_index('text', ASCENDING)


def find(token=None):
    return_list = []
    text_token = "text.{}".format(token)
    if token:
        for item in mongo_coll.find({text_token: {'$exists': True}}):
            return_list.append({'date': item['_id'],
                                'text': token,
                                'percentage': (item['text'][token]/
                                               float(sum(item['text'].values()))*100)})
    else:
        for item in mongo_coll.find():
            return_list.append({'date': item['_id'],
                                'text': sum(item['text'].values())
                                })

    return return_list
