# pylint: disable=C0114,C0116
from dataapi import main

def test_read_root():
    assert main.read_root() == {"Hello": "World"}
