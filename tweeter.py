import twitter
import yaml


config = yaml.load(file('mehfilbot.yaml', 'r'))

api = twitter.Api(
    consumer_key=config['twitter']['api_key'],
    consumer_secret=config['twitter']['api_secret'],
    access_token_key=config['twitter']['access_token'],
    access_token_secret=config['twitter']['access_token_secret']
    )


def tweet(content, reply_to_id):
    pass


def tweet_summary(summary):
    return api.PostUpdate(summary)


def tweet_item(item, reply_to_id):
    pass


def tweet_menu(menu):
    menu_items = []
    summary = "Today's Mehfil menu:\n"
    for item in menu.items()[1:]:
        summary += "{0}: {1}\n".format(
            item[0],
            item[1]['name']
            )
        menu_items.append(
            "{0}: {1} - {2} (${3})".format(
                item[0],
                item[1]['name'],
                item[1]['description'],
                item[1]['price']
                )
            )
    summary_tweet = tweet_summary(summary)
    reply_id = summary_tweet.id
    for item in menu_items:
        reply = api.PostUpdate(item, in_reply_to_status_id=reply_id)
        reply_id = reply.id
