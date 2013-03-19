#TODO: think about when an email has multiple In-Reply-To addresses

class Conversation(object):
    def __init__(self):
        self.msgs = []
        self.in_reply_to = []
        self.message_id = []

    def is_reply(self, message):
        """Check wether an email is a reply in the conversation

        The message should be an email.Message object, it is part of the
        conversation if it's a reply to one of the existing messages or if one
        of the existing messages is a reply to it
        """
        pass

    def add_msg(self, message):
        pass

    def sort(self, key):
        """Sort the emails in the conversations

        The key parameter is passed directly to list.sort(), it has the same
        significance
        """
        pass
