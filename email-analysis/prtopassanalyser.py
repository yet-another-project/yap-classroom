class PrToPassAnalyser(object):
    def __init__(self, msgs):
        """msgs argument should be a list of email.Message objects that should
        be analysed
        """
        self.msgs = [m for m in filter(self._is_pr_msg, msgs)]

    def _is_pr_msg(self, msg):
        print(msg['Subject'])
        # TODO, match:
        # case insensitive
        # [PR], peer-review, peer review

        # TODO: think about:
        # [YAP-PHPRO: 1234] [Peer-review] Exercitii
        # Re: [YAP-PHPRO: 1044] PR-exercitii


        # TODO: [YAP-PHPRO: 1507] PR pentru exercitiul "Primul cod propriu"
        # notice "PR" appearing twice above although this is a valid PR request

        # better match loosely and discard the conversations later when I check
        # for the "pass" keyword in the emails than losing valid emails from the
        # start
        return True
