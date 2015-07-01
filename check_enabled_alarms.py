#!/usr/bin/env python
import boto.ec2.cloudwatch
import argparse
import nagiosplugin
import json


disabledAlarms = list()


class Summary(nagiosplugin.Summary):
    def verbose(self, results):
        return [alarm.name for alarm in disabledAlarms]


class DisabledAlarms(nagiosplugin.Resource):
    def __init__(self, regions, key_id, key):
        self.regions = regions.split(",")
        self.key_id = key_id
        self.key = key
        if self.regions is None:
            raise TypeError("DisabledAlarms takes at least one region")

    def probe(self):
        global disabledAlarms
        for region in self.regions:
            c = boto.ec2.cloudwatch.connect_to_region(region, aws_access_key_id=self.key_id, aws_secret_access_key=self.key)
            if c is None:
                raise NetworkError("Connection Failed")
            metrics = c.describe_alarms()

            for i in metrics:
                if i.actions_enabled.lower() == 'false':
                    disabledAlarms.append(i)
        return nagiosplugin.Metric('disabledAlarms', len(disabledAlarms))


@nagiosplugin.guarded
def main():
    parser = argparse.ArgumentParser(description="Get Regions")  # Get Region from ArgsParse
    parser.add_argument("-r", dest="regions", type=str, required=True, help="set Regions to check Alarms on")
    parser.add_argument("-c", dest="file", type=str, required=True, help="AWS Access Key File")
    args = parser.parse_args()
    with open(args.file, "r") as f:
        config = json.load(f)
    check = nagiosplugin.Check(DisabledAlarms(args.regions, config["aws_access_key"], config["aws_secret_key"]), nagiosplugin.ScalarContext('disabledAlarms', 1), Summary())
    check.main()


if __name__ == '__main__':
    main()
