#! /usr/bin/env python3

import os
import email
import pickle

def get_msgs(maildir, cachefile):
    """
    TODO: Write me
    """
    mails = []
    maildir = os.path.join(os.path.abspath(os.path.expanduser(maildir)), 'cur')
    cachefile = os.path.abspath(os.path.expanduser(cachefile))

    print(maildir, cachefile)

    try:
        with open(cachefile, 'rb') as ch:
            print('from cache')
            return pickle.load(ch)

    except IOError:
        for f in os.listdir(maildir):
            with open(os.path.join(maildir, f), 'rb') as fp:
                mails.append(email.message_from_binary_file(fp))

        with open(cachefile, 'wb') as ch:
            print('to cache')
            pickle.dump(mails, ch)

        return mails


if __name__ == '__main__':
    # TODO: config file that contains the maildir path and the cache path
    msgs = []
    path = os.path.expanduser('~/Maildir/yap/phpro-book')
    msgs = get_msgs(path, 'emails.cache')

    print(len(msgs))
