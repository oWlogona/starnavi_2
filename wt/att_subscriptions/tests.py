import json

from django.contrib.auth.models import User
from django.test import TestCase
from wt.att_subscriptions.models import ATTSubscription
from wt.sprint_subscriptions.models import SprintSubscription
from rest_framework.test import APITestCase

from wt.plans.models import Plan
from wt.usage.models import DataUsageRecord, VoiceUsageRecord


class ATTSubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='oleg', password='123456')
        self.client.force_login(self.user)
        plan = Plan.objects.create(name='Plan 1', price=300, data_available=3000, created_at='2020-06-02T06:00:00',
                                   updated_at='2020-06-02T06:00:00')
        sprint_att = SprintSubscription.objects.create(user=self.user, plan=plan, status='New', device_id='111',
                                                       phone_number='number1', phone_model='model1', sprint_id=111,
                                                       effective_date='2020-06-02T06:00:00')
        att_sub_1 = ATTSubscription.objects.create(user=self.user, plan=plan, status='New', device_id='device1',
                                                   phone_number='111',
                                                   phone_model='model1', network_type='ty1',
                                                   effective_date='2020-06-04T06:00:00',
                                                   created_at='2020-06-04T06:00:00', updated_at='2020-06-04T06:00:00',
                                                   deleted=False)
        att_sub_2 = ATTSubscription.objects.create(user=self.user, plan=plan, status='New', device_id='device2',
                                                   phone_number='222',
                                                   phone_model='model2', network_type='ty2',
                                                   effective_date='2020-06-04T06:00:00',
                                                   created_at='2020-06-04T06:00:00', updated_at='2020-06-04T06:00:00',
                                                   deleted=False)
        data_usage_1 = DataUsageRecord.objects.create(att_subscription_id=att_sub_1, sprint_subscription_id=sprint_att,
                                                      price=300, usage_date='2020-06-04T06:00:00', kilobytes_used=1024)
        data_usage_2 = DataUsageRecord.objects.create(att_subscription_id=att_sub_2, sprint_subscription_id=sprint_att,
                                                      price=210, usage_date='2020-06-04T06:00:00', kilobytes_used=1024)
        voice_usage_1 = VoiceUsageRecord.objects.create(att_subscription_id=att_sub_2,
                                                        sprint_subscription_id=sprint_att,
                                                        price=147, usage_date='2020-06-03T06:00:00', seconds_used=90)

    def test_filter_by_date_status_code(self):
        request_data = {"type": "data_record", "from_d": "2020-06-02T06:00:00", "to_d": "2020-06-08T07:00:00"}
        response = self.client.post('/api/att_subscriptions/1/', request_data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_filter_by_date_current_sub_by_id(self):
        request_data = {"type": "data_record", "from_d": "2020-06-02T06:00:00", "to_d": "2020-06-08T07:00:00"}
        response = self.client.post('/api/att_subscriptions/1/', request_data, format='json')
        response_json = json.loads(json.dumps(response.data))
        self.assertEqual(type(response_json), list)
        self.assertEqual(response_json[0].get('subscription_id'), 1)
        self.assertEqual(response_json[0].get('type'), 'data_record')
        self.assertEqual(response_json[0].get('total_usage'), 300.0)

    def test_filter_by_date_other_sub(self):
        request_data = {"type": "data_record", "from_d": "2020-06-02T06:00:00", "to_d": "2020-06-08T07:00:00"}
        other_sub = [{'type': 'DataUsageRecord', 'total_usage': 210.0},
                     {'type': 'VoiceUsageRecord', 'total_usage': 147.0}]
        response = self.client.post('/api/att_subscriptions/1/', request_data, format='json')
        response_json = json.loads(json.dumps(response.data))
        self.assertEqual(response_json[0].get('other_sub'), other_sub)
