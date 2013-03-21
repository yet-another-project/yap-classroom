import bisect
import email


def comp(a, b):
    t1 = email.utils.parsedate_to_datetime(a['Date']).timestamp()
    t2 = email.utils.parsedate_to_datetime(b['Date']).timestamp()

    return t1 < t2


class Conversation(object):
    def __init__(self, message=None, key=comp):
        """Create a conversation by optionally adding message to it

        The key parameter should be a callback similar to comp(a, b), ie. it
        must be usabe as the __lt__ method of email.message.Message
        """
        self.msgs = []
        self.in_reply_tos = []
        self.messages_id = []
        self.key = key

        if message:
            self.add_msg(message)

    def is_reply(self, message):
        """Check wether an email is a reply in the conversation

        The message should be an email.Message object, it is part of the
        conversation if it's a reply to one of the existing messages or if one
        of the existing messages is a reply to it, also the message is a part
        of the conversation if it references any existing message
        """
        if message['In-Reply-To'] in self.messages_id or \
            message['Message-Id'] in self.in_reply_tos:
            return True

        if 'References' not in message.keys():
            return False

        for ref in message['References'].split():
            if ref in self.messages_id:
                return True

        return False

    def add_msg(self, message):
        # using list extend because RFC 822, 4021 and 2822  specify that the
        # In-Reply-To header may contain multiple addresses
        if 'In-Reply-To' in message.keys(): #TODO: debug here
            self.in_reply_tos.append(message['In-Reply-To'])

        self.messages_id.append(message['Message-Id'])

        # allow bisect.insort() to compare messages
        email.message.Message.__lt__ = self.key
        bisect.insort(self.msgs, message)
