#!/usr/bin/env python3
# NFCTool3 is a Python 3 implementation of the ACS-ACR122U-Tool by rocky112358
# For the original Python 2.7 version of this tool go to: https://github.com/rocky112358/ACS-ACR122U-Tool
#
# This code is licensed under the MIT license.
#
import argparse
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.ATR import ATR
from smartcard.CardType import AnyCardType
from smartcard.Exceptions import *
import sys


def main():
    global args

    parser = argparse.ArgumentParser()
    # mute, unmute, getuid, info, loadkey, read, firmver
    parser.add_argument('-ms', '--mute', action='store_true', help='Deactivate beep on card tag, default is no sound')
    parser.add_argument('-um', '--unmute', action='store_true', help='Activate beep on card tag, default is no sound')
    parser.add_argument('-u', '--get_uid', action='store_true', help='Get card UID')
    parser.add_argument('-i', '--get_info', action='store_true', help='Get card info and available protocols')
    parser.add_argument('-l', '--load', type=str, help='Load key <key> (6byte hex string) for authentication')
    parser.add_argument('-r', '--read', type=str, help='Read sector <sector> with loaded key')
    parser.add_argument('--firmware-version', action='store_true', help='Get reader firmware version')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')

    args = parser.parse_args()
    run_acs()


def run_acs():
    global args
    global connection

    connected_readers = len(reader)
    selected_reader = None

    if connected_readers == 1:
        selected_reader = reader[0]

    elif connected_readers > 1:
        for index in range(connected_readers):
            print('[{}] {}'.format(index, reader[index]))

        while not selected_reader:
            ans = input('Select an input device > ')
            try:
                index = int(ans)
                if index in range(connected_readers):
                    selected_reader = reader[index]
                    break
                else:
                    print('Sorry, there is no connected reader with that id')

            except ValueError as e:
                if args.debug:
                    print(e)
                print('That is not a valid reader id')
                pass
    else:
        print('No NFC reader was found!')
        sys.exit(0)

    try:
        # Try to connect to smart card
        connection = selected_reader.createConnection()
        connection.connect()

        sound_control(mute=True)

        if args.get_info:
            info()
        if args.load:
            loadkey(args.load)
        if args.read:
            read()
        if args.firmware_version:
            firmware()
        if args.unmute:
            sound_control(mute=False)
        if args.get_uid:
            get_uid()
    except NoCardException as e:
        if args.debug:
            print(e)
        print('Please place a card or token on the reader')


def sound_control(mute=True):
    global args

    if mute:
        base_command = [0xFF, 0x00, 0x52, 0x00, 0x00]
        status = 'Audio Off'
    else:
        base_command = [0xFF, 0x00, 0x52, 0xFF, 0x00]
        status = 'Audio On'

    parse_command(cmd=base_command, action=status)


def get_uid():
    base_command = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    parse_command(cmd=base_command, action='UID', output=True)


def info():
    global connection

    recognized_cards = {
        '00 01': 'MIFARE Classic 1K',
        '00 02': 'MIFARE Classic 4K',
        '00 03': 'MIFARE Ultralight',
        '00 26': 'MIFARE Mini',
        'F0 04': 'Topaz and Jewel',
        'F0 11': 'FeliCa 212K/424K'
    }

    if connection:
        print('[*] Tag Information\n')

        atr = ATR(connection.getATR())
        hb = toHexString(atr.getHistoricalBytes())
        name_key = hb[-17:-12]
        card_name = recognized_cards.get(name_key, 'Unknown')
        print('[+] Card Name:  ', card_name)
        print('[+] T0 Support: ', atr.isT0Supported())
        print('[+] T1 Support: ', atr.isT1Supported())
        print('[+] T15 Support:', atr.isT15Supported())


def loadkey(key):
    global args
    global connection

    base_command = [0xFF, 0x82, 0x00, 0x00, 0x06]

    if len(key.encode('utf-8')) / 2 == 6:
        # Split key into bytes and convert to integer values
        byte_list = [int(key[b: b+2], 16) for b in range(0, len(key), 2)]

        base_command.extend(byte_list)
        data, sw_one, sw_two = connection.transmit(base_command)

        if args.debug:
            print('Status words {:02x} {:02x}'.format(sw_one, sw_two))

        if (sw_one, sw_two) == (0x90, 0x00):
            print('Key {} loaded successfully'.format(key))
        elif (sw_one, sw_two) == (0x63, 0x00):
            print('Unable to load key')

    else:
        print('Unable to load key {}, length of the key must be 6 bytes long.'.format(key))


def read():
    global args
    global connection

    base_command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, int(args.read) * 4, 0x60, 0x00]

    data, sw_one, sw_two = connection.transmit(base_command)
    # Todo; finish read funcitionallity


def firmware():
    global connection

    base_command = [0xFF, 0x00, 0x48, 0x00, 0x00]

    data, sw_one, sw_two = connection.transmit(base_command)
    print('Firmware Version: {}.{}.{}'.format(''.join(chr(i) for i in data), chr(sw_one), chr(sw_two)))


def parse_command(cmd=[], action=None, output=False):
    global args
    global connection

    data, sw_one, sw_two = connection.transmit(cmd)

    if args.debug:
        print('Status code: {} {}', sw_one, sw_two)

    if output:
        print('{}: {}'.format(action, toHexString(data)))


if __name__ == '__main__':
    reader = readers()
    connection = None
    args = None

    main()
