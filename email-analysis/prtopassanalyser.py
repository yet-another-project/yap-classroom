class PrToPassAnalyser(object):
    blacklist = ('[talk]', '[meta]', '[programming]', '[sign-up]')
    whitelist = ('[pr]', 'peer review', 'peer-review')

    def __init__(self, messages):
        """messages argument should be a list of email.Message objects that should
        be analysed
        """
        #TODO: after
        #testing remove the list comprehension in order to get lazy
        #initialization
        self.msgs = [m for m in filter(self._is_pr_msg, messages)]

        print("After filter:", len(self.msgs))

    def msgs_to_conversations(self):
        pass

    def _is_pr_msg(self, msg):
        for i in self.blacklist: # using a blacklist helps me avoid false positives
            if i in msg['Subject'].lower():
                print(msg['Subject'], 'False')
                return False

        for i in self.whitelist:
            if i in msg['Subject'].lower():
                print(msg['Subject'], 'True')
                return True

        # TODO: think about:
        # Re: [YAP-PHPRO: 1044] PR-exercitii
        # [YAP-PHPRO: 1507] PR pentru exercitiul "Primul cod propriu"
        # notice "PR" appearing twice above although this is a valid PR request

        # better match loosely and discard the conversations later when I check
        # for the "pass" keyword in the emails than losing valid emails from the
        # start
        return False
