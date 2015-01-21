import twitter
import yaml


config = yaml.load(file('mehfilbot.yaml', 'r'))

api = twitter.Api(
    consumer_key=config['twitter']['api_key'],
    consumer_secret=config['twitter']['api_secret'],
    access_token_key=config['twitter']['access_token'],
    access_token_secret=config['twitter']['access_token_secret']
    )


def tweet(content, reply_to_id=None):
    if len(content) > 140:
        spaces = [i for i, ch in enumerate(content) if ch in ' \n\t']
        limit = max(index for index in spaces if index < 140)
        first_tweet = api.PostUpdate(
            content[:limit],  in_reply_to_status_id=reply_to_id)
        tweet(content[limit:], first_tweet.id)
    else:
        api.PostUpdate(content,  in_reply_to_status_id=reply_to_id)


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
    summary_tweet = tweet(summary)
    reply_id = summary_tweet.id
    for item in menu_items:
        reply = tweet(item, reply_to_id=reply_id)
        reply_id = reply.id
