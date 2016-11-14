#!/usr/bin/env python3

from pprint import pprint
import argparse
import logging

try:
    import yaml
except:
    yaml = None
import json
import sys
import os
from xml.dom import minidom
#import configParser

EXTENSIONS = {
    'json': 'json',
    'yaml': 'yaml',
    'yml': 'yaml',
    'xml': 'xml',
    'ini': 'ini',
    'conf': 'ini'
}

class UnknownFormatError(ValueError):
    pass

class ItemNotFound(NameError):
    pass

class ParseError(ValueError):
    pass

def read_data(source_file, encoding):
    if source_file:
        try:
            with open(os.path.expanduser(source_file), 'rb') as source:
                data = source.read().decode(encoding)
        except OSError, IOError, ValueError:
            logging.error('Failed to read file')
        source.cose()
    else:
        source = sys.stdin
        data = source.read()
    return data

def parse_data(data, data_format):
    if data_format == 'json':
        return json.loads(data)
    elif data_format == 'xml':
        return minidom.parseString(data)
    elif data_format == 'yaml':
        if yaml is None:
            raise UnknownFormatError('Unknown format: ' + data_format + '. Have you installed pyyaml?')
        return json.loads(data)
    else:
        raise UnknownFormatError('Unknown format: ' + data_format)

def extract(data, path):
    parts = path.split('.')

    value = data
    for part in parts:
        try:
            value = value.__getitem__(part)
        except Exception:
            raise ItemNotFound()
    return value

def get_file_format(filename, default=None):
    if not filename:
        return default
    ext = filename.split('.')[-1].lower()
    return EXTENSIONS.get(ext, default)

def main():
    parser = argparse.ArgumentParser(description='Parse and extract info.')
    parser.add_argument('source', nargs="?", help='A file source')
    parser.add_argument('--format', help='Format of data input (defaults to json if not specified by extension)')
    parser.add_argument('--extract', help='Target attribute to pull out')
    args = parser.parse_args()

    # Read data from source
    raw_data = read_data(args.source, args.decode)

    # Parse the data
    source_format = get_file_format(args.source, default='json')
    try:
        data = parse_data(raw_data, source_format)
    except UnknownFormatError as e:
        logging.error(str(e))
    except ValueError as e:
        logging.error('Error Parsing!')
        raise e

    # Extract the item
    if args.target:
        try:
            data = extract(data, args.target)
        except ItemNotFound:
            logging.error('Item "{}" not found!'.format(args.target))
            sys.exit(1)
        else:
            if not isinstance(data, dict):
                print(data)
                sys.exit(1)

    if source_format == 'json':
        print(json.dumps(data, indent=4))
    elif source_format == 'xml': 
        print(data.toprettyxml())
    else:
        print(data)

if __name__ == '__main__':
    main()
