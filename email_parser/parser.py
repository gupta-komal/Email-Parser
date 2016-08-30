import re
from imaplib import ParseFlags
from email.parser import Parser
from email.utils import parsedate_tz

from email_parser.types import Person
from email_parser.types import Mailbox
from email_parser.types import IncomingMessage, OutgoingMessage

__all__ = [
    'parse_message',
    'parse_messages'
]

LIST_RESPONSE_RE = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')


def get_message_text_and_html_part(message):
    payload = message.get_payload()

    if not isinstance(payload, (tuple, list)):
        return None, None

    text_parts = [p for p in payload if p.get_content_type() == 'text/plain']
    html_parts = [p for p in payload if p.get_content_type() == 'text/html']

    text_body, html_body = None, None

    if len(text_parts) >= 1:
        text_body = text_parts[0]

    if len(html_parts) >= 1:
        html_body = html_parts[0]

    return text_body, html_body


def build_message(message_type, uid, message, flags=None):
    if message_type not in ['incoming', 'outgoing']:
        raise ValueError('Invalid message type: %s' % (message_type))

    headers = get_message_headers(message)
    text_body, html_body = get_message_text_and_html_part(message)

    subject = headers.get('Subject', None)
    sender = headers.get('From', None)
    recipient = headers.get('To', None)

    if sender:
        sender = Person.from_string(sender)

    if recipient:
        recipient = Person.from_string(recipient)

    date_sent = headers.get('Date', None)
    date_received = headers.get('X-Received', None)

    if date_received:
        date_received = date_received.split('\n')[-1].strip()

    read = None

    if flags:
        read = '\Seen' in flags

    spf_signature = headers.get('Received-SPF', None)
    dkim_signature = headers.get('DKIM-Signature', None)

    authentication_results = headers.get('Authentication-Results', None)
    valid_spf_signature = None
    valid_dkim_signature = None

    if authentication_results:
        valid_spf_signature = 'spf=pass' in authentication_results
        valid_dkim_signature = 'dkim=pass' in authentication_results

    kwargs = {'uid': uid, 'subject': subject, 'sender': sender,
              'recipient': recipient, 'headers': headers, 'read': read,
              'text_body': text_body, 'html_body': html_body}

    if message_type == 'incoming':
        cls = IncomingMessage
        kwargs['date_sent'] = date_sent
        kwargs['date_received'] = date_received
        kwargs['spf_signature'] = spf_signature
        kwargs['dkim_signature'] = dkim_signature
        kwargs['valid_spf_signature'] = valid_spf_signature
        kwargs['valid_dkim_signature'] = valid_dkim_signature
    elif message_type == 'outgoing':
        cls = OutgoingMessage
        kwargs['date_sent'] = date_sent

    message = cls(**kwargs)
    return message


def get_message_headers(message):
    headers = {}
    keys = message.keys()

    for key in keys:
        headers[key] = message[key]

    return headers


def parse_imap_message(message_type, message_data):
    parser = Parser()
    uid = message_data[0][0]
    flags = ParseFlags(message_data[0])
    message = parser.parsestr(message_data[1])

    message = build_message(message_type=message_type, uid=uid,
                            message=message, flags=flags)
    return message


def parse_raw_message(message_type, message_data):
    parser = Parser()
    message = parser.parsestr(message_data)
    message = build_message(message_type=message_type, uid=None,
                            message=message, flags=None)
    return message


def parse_message(message_type, message_data):
    """
    Parse an email message and return Message object.
    """
    if isinstance(message_data, tuple):
        message = parse_imap_message(message_type, message_data)
    else:
        message = parse_raw_message(message_type, message_data)

    return message


def parse_messages(message_type, messages_data):
    for message_data in messages_data:
        message = parse_message(message_type, message_data)
        yield message


def parse_mailbox(line):
    """
    Parse a raw data returned by conn.list() and return Mailbox object.

    :param line: Single line from the conn.list() response.
    :type line: ``str``
    """
    flags, delimiter, name = LIST_RESPONSE_RE.match(line).groups()
    flags = flags.split(' ')
    name = name.strip('"')

    mailbox = Mailbox(name=name, flags=flags)
    return mailbox


def parse_mailboxes(data):
    """
    Parse a raw data returned by conn.list() and return a list of Mailbox
    objects.

    :param data: Raw mailbox data as returned by conn.list()
    :type data: ``list``
    """
    for line in data:
        mailbox = parse_mailbox(line)
        yield mailbox
