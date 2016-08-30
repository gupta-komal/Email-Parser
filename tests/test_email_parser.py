import os
import sys
import unittest

from os.path import join as pjoin

from email_parser.types import Person
from email_parser.parser import parse_raw_message
from email_parser.parser import parse_mailboxes
from tests.base import BaseTestCase

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = pjoin(CURRENT_DIR, 'fixtures/')
RAW_FIXTURES_DIR = pjoin(FIXTURES_DIR, 'raw/')


class EmailParserTestCase(BaseTestCase):
    fixtures_dir = RAW_FIXTURES_DIR

    def test_person_from_string(self):
        values = (
            ('Komal Gupta <komal@gmail.me>',
             ('Komal Gupta', 'komal@gmail.me')),
            ('Komal <komal@komal.me>', ('Komal', 'komal@komal.me')),
            ('<komal@komal.me>', (None, 'komal@komal.me')),
            ('komal Gupta          <komal@komal.me>',
            ('Komal Gupta', 'komal@komal.me')),
        )

        for string, expected in values:
            person = Person.from_string(string)

            self.assertEqual(person.email, expected[1])
            self.assertEqual(person.name, expected[0])

    def test_parse_incoming_raw_message_simple(self):
        fmt = '%a, %d %b %Y %H:%M:%S %Z%z'

        msg_data = self._get_fixture(name='addthis_weekly_analytics.txt')
        message = parse_raw_message('incoming', msg_data)

        self.assertEqual(message.subject, 'Your Weekly AddThis Analytics')
        self.assertEqual(message.sender.email, 'support@addthis.com')
        self.assertEqual(message.sender.name, 'AddThis Team')
        self.assertEqual(message.recipient.email, 'komal+coachspree@komal.me')

        self.assertEqual(message.date_sent.strftime(fmt),
                         'Sun, 18 Aug 2013 18:41:25 +0000')
        self.assertEqual(message.date_received.strftime(fmt),
                         'Sun, 18 Aug 2013 11:41:26 -0700')

        self.assertEqual(message.read, None)
        self.assertTrue(message.valid_spf_signature)
        self.assertTrue(message.valid_dkim_signature)


class MailboxParseTestCase(BaseTestCase):
    fixtures_dir = pjoin(FIXTURES_DIR, 'imap/')

    def test_parse_mailboxes(self):
        data = eval(self._get_fixture(name='conn.list_1.txt'))[1]
        mailboxes = list(parse_mailboxes(data))

        self.assertEqual(mailboxes[0].name, 'INBOX')
        self.assertEqual(mailboxes[0].flags, ['\\HasNoChildren'])
        self.assertEqual(mailboxes[6].name, '[Gmail]/Spam')
        self.assertEqual(mailboxes[6].flags, ['\\HasNoChildren', '\\Junk'])


if __name__ == '__main__':
    sys.exit(unittest.main())
