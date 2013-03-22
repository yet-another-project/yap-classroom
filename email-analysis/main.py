#! /usr/bin/env python3

import os
import email
import pickle
import configparser

import prconversationlist as pcl
from helpers import strip_from_header, get_email_body


def get_msgs_from_cache(cachefile):
    with open(cachefile, 'rb') as ch:
        return pickle.load(ch)


def set_cache(cachefile, data):
    with open(cachefile, 'wb') as ch:
        pickle.dump(data, ch)


def get_msgs(maildir, cachefile):
    """Return a list of email.Message objects after parsing the emails found in
    maildir or by getting them directly from the pickled cachefile
    """
    mails = []
    maildir = os.path.join(maildir, 'cur')

    try:
        mails = get_msgs_from_cache(cachefile)
    except IOError:
        for f in os.listdir(maildir):
            with open(os.path.join(maildir, f), 'rb') as fp:
                mails.append(email.message_from_binary_file(fp)) #TODO: insort()

        set_cache(cachefile, mails)

    return mails


def get_pass_mail(conversation):
    """Return the email where the student got "pass" in the conversation passed
    as parameter
    """
    for m in reversed(conversation.msgs[1:]):
        if 'pass' in get_email_body(m).lower():
            # if the conversation is generated by PronversationList it is
            # guaranteed that it will contain a "pass"
            return m


def analyse_prtopass(c):
    """c is a conversation which should be mined for data

    This function returns a dictionary with the following geometry:
    {
    'student': the student who requested the pass
    'tutor': the tutor that possibly guided the user by giving him "pass"
    'req_date': the peer review request datetime
    'pass_date': the datetime when the student got "pass"
    'exercise': the exercise to which the user requested peer review
    }
    """
    data = {}
    data['student'] = strip_from_header(c.msgs[0]['From'])
    data['req_date'] = email.utils.parsedate_to_datetime(c.msgs[0]['Date'])

    pass_mail = get_pass_mail(c)
    data['tutor'] = strip_from_header(pass_mail['From'])
    data['pass_date'] = email.utils.parsedate_to_datetime(pass_mail['Date'])

    data['exercise'] = c.msgs[0]['Subject']

    return data


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    maildir = os.path.abspath(os.path.expanduser(config['paths']['maildir']))
    cache = os.path.abspath(os.path.expanduser(config['paths']['cachefile']))

    msgs = []
    msgs = get_msgs(maildir, cache)

    total_no_msgs = len(msgs)

    msgs.sort(key=lambda x: email.utils.parsedate_to_datetime(x['Date']).timestamp())

    pr_convs = pcl.PrConversationList(msgs)
    pr_no_convs = len(pr_convs)

    data = map(analyse_prtopass, pr_convs)

    total_hours = 0
    for d in data:
        delta = d['pass_date'] - d['req_date']
        hours_to_pass = delta.total_seconds()/3600
        total_hours += hours_to_pass

    print((
    "              | #PR\t\t#Total\n"
    "-----------------------------------------------------------------------\n"
    "Messages      | {0} {1:>16}\n"
    "Out of {0} PR messages:\n"
    "Conversations | {2} {3:>15}\n\n\n"

    "#Mean PR to PASS hrs\t\t#Total PR to PASS hrs\n"
    "-----------------------------------------------------------------------\n"
    "{4:.2f} {5:>33.2f}"
    ).format(pr_convs.no_msgs, total_no_msgs, pr_no_convs,
        pr_convs.total_no_conversations, total_hours/pr_no_convs, total_hours))
