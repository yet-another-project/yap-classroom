import conversation as conv

class PrToPassAnalyser(object):
    blacklist = ('[talk]', '[meta]', '[programming]', '[sign-up]')
    whitelist = ('[pr]', 'peer review', 'peer-review')

    def __init__(self, messages):
        """messages param should be a list of email.Message objects that will
        be analysed
        """
        #TODO: after
        #testing remove the list comprehension in order to get lazy
        #initialization
        self.msgs = [m for m in filter(self._is_pr_msg, messages)]
        #self.msgs = filter(self._is_pr_msg, messages)
        self.conversations = []

        print("After filter:", len(self.msgs))

    def msgs_to_conversations(self):
        for m in self.msgs:
            for c in self.conversations:
                if c.is_reply(m):
                    c.add_msg(m)
                    break
            else: # no conversation found for this message, creating one
                self.conversations.append(conv.Conversation(m))

        print("No. conv:", len(self.conversations))

    def _is_pr_msg(self, msg):
        """Try to separate the emails that are asking for peer-review
        (these are the ones we're intrested about in this class)
        """
        # using a blacklist helps me avoid false positives
        for i in self.blacklist:
            if i in msg['Subject'].lower():
                return False

        for i in self.whitelist:
            if i in msg['Subject'].lower():
                return True

        # TODO: think about:
        # Re: [YAP-PHPRO: 1044] PR-exercitii
        # [YAP-PHPRO: 1507] PR pentru exercitiul "Primul cod propriu"
        # notice "PR" appearing twice above although this is a valid PR request

        # better match loosely and discard the conversations later when I check
        # for the "pass" keyword in the emails than losing valid emails from
        # the start
        return False
