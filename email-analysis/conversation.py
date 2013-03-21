class Conversation(object):
    def __init__(self, message=None):
        """Create a conversation by optionally adding message to it

        The key parameter should be a callback similar to comp(a, b), ie. it
        must be usabe as the __lt__ method of email.message.Message
        """
        self.msgs = []
        self.refs = []  # TODO: use a set not a list

        if message:
            self.add_msg(message)

    def is_reply(self, message):
        """Check wether an email is a reply in the conversation

        The message should be an email.Message object, it is part of the
        conversation if it's a reply to one of the existing messages or if one
        of the existing messages is a reply to it, also the message is a part
        of the conversation if it references any existing message
        """
        if message['In-Reply-To'] in self.refs or \
            message['Message-Id'] in self.refs:
            return True

        if 'References' not in message.keys():
            return False

        for ref in message['References'].split():
            if ref in self.refs:
                return True

        return False

    def add_msg(self, message):
        # using list extend because RFC 822, 4021 and 2822  specify that the
        # In-Reply-To header may contain multiple addresses
        if 'In-Reply-To' in message.keys():
            self.refs.extend(message['In-Reply-To'].split())

        if 'References' in message.keys():
            self.refs.extend(message['References'].split())

        self.refs.append(message['Message-Id'])

        self.msgs.append(message)
