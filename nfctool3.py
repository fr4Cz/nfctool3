#!/usr/bin/env python3
import argparse
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.ATR import ATR
from smartcard.CardType import AnyCardType
import sys


def main():
    parser = argparse.ArgumentParser()
    # mute, unmute, getuid, info, loadkey, read, firmver
    parser.add_argument('-ms', '--mute', action='store_true', help='Deactivate beep on card tag, default is no sound')
    parser.add_argument('-ls', '--loud', action='store_true', help='Activate beep on card tag, default is no sound')
    parser.add_argument('-g', '--get_uid', action='store_true', help='Get card UID')
    parser.add_argument('-i', '--get_info', action='store_true', help='Get card info and available protocols')
    parser.add_argument('-l', '--load', type=str, help='Load key <key> (6byte hex string) for authentication')
    parser.add_argument('-r', '--read', type=str, help='Read sector <sector> with loaded key')
    parser.add_argument('--firmware-version', action='store_true', help='Get reader firmware version')

    args = parser.parse_args()
    run_acs(args)


def run_acs(args):
    connected_readers = len(reader)
    if connected_readers == 1:
        print(reader[0])
    elif connected_readers > 1:
        # Select reader
        pass
    else:
        print('No NFC reader was found!')
        sys.exit(0)


def sound_control():
    pass


def get_uid():
    pass


def info():
    pass


def loadkey():
    pass


def read():
    pass


def firmware():
    pass


if __name__ == '__main__':
    reader = readers()
    main()
