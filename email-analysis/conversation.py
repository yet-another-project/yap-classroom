class Conversation(object):
    def __init__(self, message=None):
        self.msgs = []
        self.in_reply_tos = []
        self.messages_id = []

        if message:
            self.add_msg(message)

    def is_reply(self, message):
        """Check wether an email is a reply in the conversation

        The message should be an email.Message object, it is part of the
        conversation if it's a reply to one of the existing messages or if one
        of the existing messages is a reply to it
        """
        pass

    def add_msg(self, message):
        # using list extend because RFC 822, 4021 and 2822  specify that the
        # In-Reply-To header may contain multiple addresses
        if 'In-Reply-To' in message.keys():
            self.in_reply_tos.extend(message['In-Reply-To'])

        self.messages_id.append(message['Message-Id'])
        self.msgs.append(message)

    def sort(self, key):
        """Sort the emails in the conversations

        The key parameter is passed directly to list.sort(), it has the same
        significance
        """
        pass
