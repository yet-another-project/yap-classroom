def strip_from_header(from_header):
    """An email 'From' header looks like:
    "Paul Barbu Gh." <paullik.paul@gmail.com>

    What this function does is to return the email address in between < and >
    """
    return from_header[from_header.rfind(' ')+1:].strip('<').strip('>')


def get_email_body(email):
    if not email.is_multipart():
        return email.get_payload()

    # lucky guess that the actual body is the first part in the message
    return get_email_body(email.get_payload()[0])
