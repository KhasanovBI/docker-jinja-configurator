#!/usr/bin/env python
from __future__ import unicode_literals

import argparse
import json
import os
import sys
from glob import glob

from j2cli.cli import render_command
from jsonschema import validate

SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'template': {'type': 'string'},
            'data': {'type': 'string'},
            'destination': {'type': 'string'},
        },
        'required': ['template', 'destination'],
    }
}


def get_data_filepath(data_dir, clean_rel_template_filepath):
    data_filepath_start = os.path.join(data_dir, clean_rel_template_filepath)
    matches = glob('{data_filepath_start}.*'.format(data_filepath_start=data_filepath_start))
    if len(matches) == 0:
        return None

    if len(matches) > 1:
        raise IOError('Multiple matches {} for pattern {}'.format(matches, data_filepath_start))

    return matches[0]


def prepare_file_mappings(templates_dir, data_dir, output_dir):
    mappings = []
    for root, dirs, filenames in os.walk(templates_dir):
        for filename in filenames:
            template_filepath = os.path.join(root, filename)
            rel_template_filepath = os.path.relpath(template_filepath, templates_dir)
            if rel_template_filepath.endswith('.j2'):
                clean_rel_template_filepath = os.path.splitext(rel_template_filepath)[0]
            else:
                clean_rel_template_filepath = rel_template_filepath
            data_filepath = get_data_filepath(data_dir, clean_rel_template_filepath)
            destination_filepath = os.path.join(output_dir, clean_rel_template_filepath)
            mappings.append({
                'template': template_filepath,
                'data': data_filepath,
                'destination': destination_filepath,
            })
    return mappings


def core(config):
    if not config.mappings_file:
        mappings = prepare_file_mappings(config.templates_dir, config.data_dir, config.output_dir)
    else:
        mappings = json.load(config.mappings_file)
        validate(mappings, SCHEMA)
    for mapping in mappings:
        template_filepath = mapping['template']
        data_filepath = mapping.get('data')
        destination_filepath = mapping['destination']

        print('Process template: {}, data: {}, destination: {}'.format(
            template_filepath,
            data_filepath,
            destination_filepath
        ))

        args = [template_filepath]
        if data_filepath:
            args.append(data_filepath)
        output = render_command(
            os.getcwd(),
            os.environ,
            sys.stdin,
            args
        )

        destination_dir = os.path.dirname(destination_filepath)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        with open(destination_filepath, 'w') as f:
            f.write(output)


def check_dir_existence(dir_):
    if not os.path.isdir(dir_):
        raise IOError('Invalid directory \'%s\'' % dir_)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Render templates.')
    parser.add_argument(
        '-o',
        '--output-dir',
        type=str,
        default='/output/',
        required=True,
        help='path to rendered templates output dir',
    )
    parser.add_argument(
        '-t',
        '--templates-dir',
        type=str,
        default='/templates/',
        help='path to templates dir',
    )
    parser.add_argument(
        '-d',
        '--data-dir',
        type=str,
        default='/data/',
        help='path to data variables dir',
    )
    parser.add_argument(
        '-m',
        '--mappings-file',
        type=argparse.FileType('r'),
        help='path to mappings file',
    )
    parsed_args = parser.parse_args(args)

    if not parsed_args.mappings_file:
        for dir_ in (parsed_args.templates_dir, parsed_args.data_dir):
            check_dir_existence(dir_)
    return parsed_args


if __name__ == '__main__':
    core(parse_args())
