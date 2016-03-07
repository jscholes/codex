# Codex
# Copyright (C) 2015 James Scholes
# This program is free software, licensed under the terms of the GNU General Public License (version 3 or later).
# See the file LICENSE.txt for more details.

import os.path
import struct


FIRST_RECORD_INFO_OFFSET = 78


class KindleMetadataError(Exception):
    pass


def get_title_and_author_from_kindle_file(path):
    stream = open(path, 'rb')

    format_header = stream.read(3)
    if b'TPZ' in format_header:
        raise KindleMetadataError

    try:
        record_zero = get_record(0, stream)
        exth_header = get_exth_header(record_zero)
        metadata_records = get_metadata_from_exth_header(exth_header)
        if 'title' not in metadata_records.keys():
            metadata_records['title'] = os.path.basename(path)
        return metadata_records
    except struct.Error:
        raise KindleMetadataError


def get_record(record_number, stream):
    record_info_offset = get_record_info_offset(0)
    record_data_offset = get_record_data_offset(record_info_offset, stream)
    next_record_info_offset = get_record_info_offset(1)
    next_record_data_offset = get_record_data_offset(next_record_info_offset, stream)
    stream.seek(record_data_offset)
    return stream.read(next_record_data_offset - record_data_offset)


def get_record_info_offset(record_number):
    record_info_offset = FIRST_RECORD_INFO_OFFSET + (8 * record_number)
    return record_info_offset


def get_record_data_offset(record_info_offset, stream):
    stream.seek(record_info_offset)
    record_data_offset = struct.unpack('>i', stream.read(4))[0]
    return record_data_offset


def get_exth_header(record_zero):
    mobi_header_length = get_mobi_header_length(record_zero)
    exth_header_offset = mobi_header_length + 16
    exth_header_length = get_exth_header_length(exth_header_offset, record_zero)
    return record_zero[exth_header_offset:exth_header_offset + exth_header_length]


def get_mobi_header_length(record_zero):
    return struct.unpack('>i', record_zero[20:24])[0]


def get_exth_header_length(exth_header_offset, record_zero):
    exth_header_length_offset = exth_header_offset + 4
    return struct.unpack('>i', record_zero[exth_header_length_offset:exth_header_length_offset + 4])[0] + 16


def get_metadata_from_exth_header(exth_header):
    record_count = get_number_of_exth_records(exth_header)
    metadata_records = get_metadata_records(record_count, exth_header)
    return metadata_records


def get_number_of_exth_records(exth_header):
    return struct.unpack('>i', exth_header[8:12])[0]


def get_metadata_records(record_count, exth_header):
    metadata_records = {}
    exth_identifiers = {100: 'author', 503: 'title'}
    current_record = 1
    current_offset = 12
    while current_record <= record_count:
        record_type = get_record_type(current_offset, exth_header)
        record_length = get_record_length(current_offset, exth_header)
        if record_type in exth_identifiers:
            metadata_records[exth_identifiers[record_type]] = get_record_data(current_offset, record_length, exth_header)
            current_record += 1
            current_offset += record_length
        else:
            current_record += 1
            current_offset += record_length
            continue

    return metadata_records


def get_record_type(offset, exth_header):
    record_type = struct.unpack('>i', exth_header[offset:offset + 4])[0]
    return record_type


def get_record_length(offset, exth_header):
    record_length = struct.unpack('>i', exth_header[offset + 4:offset + 8])[0]
    return record_length


def get_record_data(offset, record_length, exth_header):
    data_length = record_length - 8
    record_data = struct.unpack('>{0}s'.format(data_length), exth_header[offset + 8:offset + 8 + data_length])[0].decode('utf-8', errors='replace').replace('\x00', '')
    return record_data


