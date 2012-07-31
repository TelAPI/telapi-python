import unittest
import os
import json
import time
from telapi import rest

class TestREST(unittest.TestCase):
    def setUp(self):
        # Environment variables must be set for TELAPI_ACCOUNT_SID and TELAPI_AUTH_TOKEN
        self.client = rest.Client(base_url='https://api.dev.telapi.com/2011-07-01/')
        # self.client = rest.Client()
        self.test_cell_number = os.environ.get('TELAPI_TEST_NUMBER')

        if not os.environ.get('TELAPI_ACCOUNT_SID'):
            raise Exception("Please set the TELAPI_ACCOUNT_SID, TELAPI_AUTH_TOKEN and TELAPI_TEST_NUMBER environment variables to run the tests!")


    # Test REST Client getattr
    def test_bad_resource_list_resource(self):
        with self.assertRaises(AttributeError):
            self.client.bad_resource_name

    def test_account_list_resource(self):
        accounts = self.client.accounts
        self.assertEquals(accounts.__class__.__name__, 'AccountListResource')
        self.assertEquals(accounts._url, 'Accounts')

        # Make sure the list resource doesn't have instance resource params
        with self.assertRaises(AttributeError):
            accounts.sid

        # Bad property name
        with self.assertRaises(AttributeError):
            accounts.random_property_name

        # Dict-style key access
        account = accounts[self.client.account_sid]

        # Check types and generated URLs
        self.assertEquals(account.__class__.__name__, 'Account')
        self.assertEquals(account._url, 'Accounts/' + self.client.account_sid)
        self.assertEquals(account.sid, self.client.account_sid)
        self.assertEquals(account.status, 'active')

    def test_notifications_list_resource(self):
        account = self.client.accounts[self.client.account_sid]
        notifications = account.notifications
        self.assertEquals(notifications.__class__.__name__, 'NotificationListResource')

        # len()
        self.assertTrue(len(notifications))

        # Negative Indexes
        notifications[-1]

        # Iteration
        for notification in notifications:
            notification.request_url

        # Slicing
        for notification in notifications[10:20]:
            notification.request_url

        for notification in notifications[1:5:-1]:
            notification.request_url

        # Disallow setattr
        with self.assertRaises(TypeError):
            notifications[0] = 5

    def test_pagination(self):
        test_dir = os.path.dirname(__file__)
        accounts_data = json.load(open(os.path.join(test_dir, 'test_accounts.json')))

        # Internal call to use dummy data
        accounts = self.client.accounts[10:20]
        accounts.fetch(resource_data=accounts_data)

        for i, account in enumerate(accounts):
            self.assertIsNotNone(account.sid)

        self.assertEquals(i, 9)
        
        # Internal call to use dummy data
        accounts = self.client.accounts[20:40]
        accounts.fetch(resource_data=accounts_data)

        for i, account in enumerate(accounts):
            self.assertIsNotNone(account.sid)

        self.assertEquals(i, 19)

    def test_sms_list(self):
        sms_list = self.client.accounts[self.client.account_sid].sms_messages[:100]

        for i, sms in enumerate(sms_list):
            self.assertTrue(sms.body)
            self.assertTrue(sms.from_number)
            self.assertTrue(sms.to_number)

        self.assertEquals(i + 1, len(sms_list))

    def test_sms_send(self):
        sms_list = self.client.accounts[self.client.account_sid].sms_messages
        from_number = to_number = self.test_cell_number
        body = "Hello from telapi-python!"
        sms = sms_list.create(from_number=from_number, to_number=to_number, body=body)
        self.assertTrue(sms.sid.startswith('SM'))
        self.assertEquals(sms.body, body)
        self.assertEquals(sms.from_number, from_number)
        self.assertEquals(sms.to_number, to_number)

    def test_incoming_phone_numbers(self):
        account = self.client.accounts[self.client.account_sid]

        # Test listing
        for number in account.incoming_phone_numbers:
            self.assertTrue(number.phone_number.startswith('+'))


        # Make sure there's no exception when there's no results
        no_available_numbers = account.available_phone_numbers.filter(AreaCode=999)
        # self.assertEquals(len(no_available_numbers), 0)

        for number in no_available_numbers:
            print no_available_numbers.phone_number


        # Filter and buy a DID
        available_numbers = account.available_phone_numbers.filter(AreaCode=435)
        self.assertTrue(len(available_numbers))

        for number in available_numbers:
            self.assertEquals(number.phone_number[:5], '+1435')
            self.assertEquals(number.npa, "435")
            self.assertEquals(number.country_code, "+1")

        good_available_number = available_numbers[0]
        phone_number = good_available_number.phone_number
        purchase_number = account.incoming_phone_numbers.create(phone_number=phone_number)


        # Try to update
        purchase_number.voice_url = voice_url = "http://db.tt/YtLJgpa8"
        purchase_number.save()


        # Make sure the number is in the list (clear the cache with .clear first)
        found = False
        
        for number in account.incoming_phone_numbers.clear():
            if number.phone_number == phone_number and number.voice_url.strip() == voice_url:
                found = True
                break

        self.assertTrue(found)


        # Delete the number
        purchase_number.delete()


        # Make sure the number is no longer in the list
        found = False
        for number in account.incoming_phone_numbers:
            if number.phone_number == phone_number and number.voice_url == voice_url:
                found = True
                break

        self.assertTrue(not found)

    def test_calls(self):
        account = self.client.accounts[self.client.account_sid]

        # Typecast to list to make sure enumeration works
        list(account.calls)

        # Use alternate syntax to create to update properties before saving
        call = account.calls.new()
        call.from_number = "+19492660933"
        call.to_number = "+17328381916"
        call.url = "https://dl.dropbox.com/u/14573179/TML/wait_music.xml"

        # Dial
        call.save()

        # Wait a bit
        time.sleep(20)

        # Hangup
        call.status = "Completed"
        call.save()


if __name__ == '__main__':
    unittest.main()
