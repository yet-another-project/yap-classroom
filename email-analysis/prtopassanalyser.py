import conversation as conv
from helpers import strip_from_header, get_email_body


class PrToPassAnalyser(object):
    blacklist = ('[talk]', '[meta]', '[programming]', '[sign-up]')
    whitelist = ('[pr]', 'peer review', 'peer-review')

    def __init__(self, messages):
        """messages param should be a list of email.Message objects that will
        be analysed
        """
        self.msgs = filter(self._is_pr_msg, messages)
        self.conversations = []
        self.total_no_conversations = 0
        self.pr_no_conversations = 0
        self.total_no_msgs = 0
        self.pr_no_msgs = 0

    def msgs_to_conversations(self):
        """Populate the self.conversations list with Conversation objects

        We assume that the messgaes are sorted chronologically when passed to
        this class otherwise the outer for should be done while changes still
        happen in the conversations, so that all the messages are included in
        the right conversations
        """
        self.total_no_msgs = 0
        self.pr_no_msgs = 0

        for m in self.msgs:
            for c in self.conversations:
                if c.is_reply(m):
                    c.add_msg(m)
                    break
            else:  # no conversation found for this message, creating one
                self.conversations.append(conv.Conversation(m))

        self.total_no_conversations = len(self.conversations)

    def gather_conversations_data(self):
        self.pr_no_conversations = 0
        for c in self.conversations:
            if self.is_valid_conversation(c):
                # TODO: author, tutor(s), time to pass, exercise, etc
                self.pr_no_conversations += 1
                pass

    def _is_pr_msg(self, msg):
        """Try to separate the emails that are asking for peer-review
        (these are the ones we're intrested about in this class)
        """
        self.total_no_msgs += 1

        # using a blacklist helps me avoid false positives
        for i in self.blacklist:
            if i in msg['Subject'].lower():
                return False

        for i in self.whitelist:
            if i in msg['Subject'].lower():
                self.pr_no_msgs += 1
                return True

        # TODO: think about:
        # Re: [YAP-PHPRO: 1044] PR-exercitii
        # [YAP-PHPRO: 1507] PR pentru exercitiul "Primul cod propriu"
        # notice "PR" appearing twice above although this is a valid PR request

        # better match loosely and discard the conversations later when I check
        # for the "pass" keyword in the emails than losing valid emails from
        # the start
        return False

    def is_valid_conversation(self, c):
        """A conversation is considered valid only if it has more than one
        message and if a tutor replied with a "pass"

        This method (same as msgs_to_conversations()) assumes that the messages
        are already sorted chronologically, otherwise student won;t be the
        student who requested the peer review
        """
        if len(c.msgs) <= 1:
            return False

        student = strip_from_header(c.msgs[0]['From'])
        for m in c.msgs[1:]:
            author = strip_from_header(m['From'])

            if 'pass' in get_email_body(m).lower() and author != student:
                return True

        return False

    def print_stats(self):
        print("{0}/{1} pr/total msgs".format(
            self.pr_no_msgs, self.total_no_msgs))
        print("{0}/{1} pr/total conv".format(
            self.pr_no_conversations, self.total_no_conversations))
