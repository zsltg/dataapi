import argparse

from tests import test_base

parser = argparse.ArgumentParser(description="Generate dialogs in bulk")
parser.add_argument("-u", type=int, help="Number of customers (default is 100)", default=100)
parser.add_argument("-d", type=int, help="Number of dialogs (default is 1000)", default=1000)
parser.add_argument("-c", type=int, help="Number of consents (default is 500)", default=500)
args = parser.parse_args()

base_test = test_base.BaseTest()
base_test._bulk_customer_count = args.u
base_test._bulk_dialog_count = args.d
base_test._bulk_consent_count = args.c
base_test.setUp()