#! /usr/bin/env python3

import os
import email
import pickle
import configparser

import prtopassanalyser as ppa


def get_msgs_from_cache(cachefile):
    with open(cachefile, 'rb') as ch:
        print('from cache')
        return pickle.load(ch)


def set_cache(cachefile, data):
    with open(cachefile, 'wb') as ch:
        print('to cache')
        pickle.dump(data, ch)


def get_msgs(maildir, cachefile):
    """Return a list of email.Message objects after parsing the emails found in
    maildir or by getting them directly from the pickled cachefile
    """
    mails = []
    maildir = os.path.join(maildir, 'cur')

    print(maildir, cachefile)

    try:
        mails = get_msgs_from_cache(cachefile)
    except IOError:
        for f in os.listdir(maildir):
            with open(os.path.join(maildir, f), 'rb') as fp:
                mails.append(email.message_from_binary_file(fp)) #TODO: insort()

        set_cache(cachefile, mails)

    return mails


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    maildir = os.path.abspath(os.path.expanduser(config['paths']['maildir']))
    cache = os.path.abspath(os.path.expanduser(config['paths']['cachefile']))

    msgs = []
    msgs = get_msgs(maildir, cache)

    msgs.sort(key=lambda x: email.utils.parsedate_to_datetime(x['Date']).timestamp())

    pr = ppa.PrToPassAnalyser(msgs)
    pr.msgs_to_conversations()
    pr.gather_conversations_data()
    pr.print_stats()
