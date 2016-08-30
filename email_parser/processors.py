class NewsletterProcessor(object):
    def __init__(self, messages):
        self.messages = messages


class NewsletterSubscription(object):
    def __init__(self, name, sender, first_email_date, total_count=None,
                 read_count=None, unread_count=None, unsubscribe_link=None):
        self.name = name
        self.sender = sender
        self.first_email_date = first_email_date
        self.total_count = total_count
        self.read_count = read_count
        self.unread_count = unread_count
        self.unsubscribe_link = unsubscribe_link
