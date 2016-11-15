#!/usr/bin/env python3

import argparse
import base64
import string
import random
import uuid
import sys
import os

def random_bytes(size):
    return os.urandom(size)

def to_b64_str(the_bytes, encoding='utf-8'):
    return base64.b64encode(the_bytes).decode(encoding)

def from_b64_str(string, encoding='utf-8'):
    return base64.b64decode(string.encode(encoding))

#############
### Commands

def generate_byte_key(args):
    key_bytes = random_bytes(args.length)
    if args.encode:
        print(to_b64_str(key_bytes))
    else:
        sys.stdout.buffer.write(key_bytes)

def generate_uuid(args):
    print(uuid.UUID(bytes=random_bytes(16)))

def generate_random_string(args):
    sys_random = random.SystemRandom()
    selections = [sys_random.choice(args.source) for i in range(args.length)]
    print(''.join(selections))

#############
### Parser

def main():
    main_parser = argparse.ArgumentParser(prog='Key Generator (Sourced by urandom)')
    subparsers = main_parser.add_subparsers()

    byte_key_gen = subparsers.add_parser('key', help='Random bytes generated for a key')
    byte_key_gen.add_argument('-l', '--length', dest='length', type=int, help='length of key in bytes', default=16)
    byte_key_gen.add_argument('-e', '--encode', dest='encode', action='store_true', help='Encode bytes into base64 string', default=False)
    byte_key_gen.set_defaults(func=generate_byte_key)

    uuid_parser = subparsers.add_parser('uuid', help='Random UUID')
    uuid_parser.set_defaults(func=generate_uuid)

    random_str_parser = subparsers.add_parser('string', help='Random string')
    random_str_parser.add_argument('--source', help='Characters to select from (defaults to alpha-numeric)', default=string.ascii_letters + string.digits)
    random_str_parser.add_argument('--length', type=int, help='Length of string', default=20)
    random_str_parser.set_defaults(func=generate_random_string)

    args = main_parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
