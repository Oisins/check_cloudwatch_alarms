#!/usr/bin/env python
import unittest
import boto.ec2.cloudwatch
import nagiosplugin
from mock import Mock
from check_enabled_alarms import DisabledAlarms


CONNECT_TO_REGION_RESULT = 'true'
REGIONS = ['eu-west-1', 'us-east-1', 'sa-east-1']
AWS_ACCESS_KEY_ID = "ABC"
AWS_SECRET_ACCESS_KEY = "ABC"


MetricsMockTrue = Mock()
MetricsMockTrue.actions_enabled = 'true'

MetricsMockFalse = Mock()
MetricsMockFalse.actions_enabled = 'false'

ConnectionMock = Mock()
ConnectionMock.describe_alarms.return_value = [MetricsMockFalse, MetricsMockTrue, MetricsMockFalse]


class DisabledAlarmsTest(unittest.TestCase):
    def test_probe(self):
        boto.ec2.cloudwatch.connect_to_region = Mock(return_value=ConnectionMock)
        x = DisabledAlarms(REGIONS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        result = x.probe()
        self.assertEquals(result, nagiosplugin.Metric('disabledAlarms', 2 * len(REGIONS)))


if __name__ == '__main__':
    unittest.main()
