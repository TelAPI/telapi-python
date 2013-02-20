import unittest
import json
from mock import patch
from telapi import rest
from telapi.schema import SCHEMA

class TestREST(unittest.TestCase):


    def setUp(self):
        self.test_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        self.test_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        self.test_number = '+17325551234'
        self.client = rest.Client(base_url='https://api.telapi.com/v1/', account_sid=self.test_sid, auth_token=self.test_token)


    def test_bad_resource_list_resource(self):
        with self.assertRaises(AttributeError):
            self.client.bad_resource_name


    def test_bad_credentials_account(self):
        with self.assertRaises(rest.exceptions.AccountSidError):
            rest.Client(account_sid='abc123')


    def test_bad_credentials_token(self):
        with self.assertRaises(rest.exceptions.AuthTokenError):
            rest.Client(account_sid=self.test_sid, auth_token='abc123')

    #
    #  - Accounts -  
    #
    @patch("telapi.rest.Client._send_request")
    def test_account_resource(self, mock):

        mock.return_value = json.load(open('mock-response/view-account.json','r'))

        accounts = self.client.accounts

        self.assertEqual(accounts.__class__.__name__, 'AccountListResource')
        self.assertEqual(accounts._url, 'Accounts')

        # Make sure the list resource doesn't have instance resource params
        with self.assertRaises(AttributeError):
            accounts.sid

        # Bad property name
        with self.assertRaises(AttributeError):
            accounts.random_property_name

        # Dict-style key access
        account = accounts[self.client.account_sid]

        # Check types and generated URLs
        self.assertEqual(account.__class__.__name__, 'Account')
        self.assertEqual(account._url, 'Accounts/' + self.client.account_sid)

        # Check attribute access
        self.assertEqual(account.status, 'active')
        self.assertEqual(account.sid, self.client.account_sid)

        # Check schema attribute accuracy
        self.assertEqual(set(SCHEMA["rest_api"]["components"].get('accounts')['attributes']), set(account._resource_data.keys()))



    #
    #  - SMS -
    #
    @patch("telapi.rest.Client._send_request")
    def test_sms_resource(self, mock):

        mock.return_value = json.load(open('mock-response/list-sms.json','r'))

        #check filter()
        sms_list = self.client.accounts[self.client.account_sid].sms_messages.filter(From='+17325551234')

        # Check attribute access
        for i, sms in enumerate(sms_list):
            self.assertTrue(sms.body)
            self.assertTrue(sms.from_number)
            self.assertTrue(sms.to_number)


    @patch("telapi.rest.Client._send_request")
    def test_sms_send(self, mock):

        mock.return_value = json.load(open('mock-response/send-sms.json','r'))

        from_number = to_number = self.test_number
        body = "Hello from telapi python!"
        sms = self.client.accounts[self.client.account_sid].sms_messages.create(from_number=from_number, to_number=to_number, body=body)

        self.assertTrue(sms.sid.startswith('SM'))
        self.assertEquals(sms.body, body)
        self.assertEquals(sms.from_number, from_number)
        self.assertEquals(sms.to_number, to_number)

        # Check schema attribute accuracy
        self.assertEqual(set(SCHEMA["rest_api"]["components"].get('sms_messages')['attributes']), set(sms._resource_data.keys()))


    #
    #  - Notifications -
    #
    @patch("telapi.rest.Client._send_request")
    def test_notifications_resource(self, mock):

        mock.return_value = json.load(open('mock-response/list-notifications.json','r'))

        notifications = self.client.accounts[self.client.account_sid].notifications

        self.assertEqual(notifications.__class__.__name__, 'NotificationListResource')

        # len()
        self.assertTrue(len(notifications))

        # Iteration
        for notification in notifications:
            self.assertTrue(notification.sid)

        # Slicing
        for notification in notifications[0:6]:
            self.assertTrue(notification.sid)

        for notification in notifications[1:5:-1]:
            self.assertTrue(notification.sid)

        # Disallow setattr
        with self.assertRaises(TypeError):
            notifications[0] = 5




if __name__ == '__main__':
    unittest.main()