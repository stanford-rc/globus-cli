from __future__ import print_function

import json

from globus_sdk import TransferClient
from globus_cli import version
from globus_cli.helpers import text_header_and_format


def get_client():
    return TransferClient(app_name=version.app_name)


def display_name_or_cname(ep_doc):
    return ep_doc['display_name'] or ep_doc['canonical_name']


def print_json_from_iterator(iterator):
    json_output_dict = {'DATA': []}
    for item in iterator:
        dat = item
        try:
            dat = item.data
        except AttributeError:
            pass
        json_output_dict['DATA'].append(dat)
    print(json.dumps(json_output_dict, indent=2))


def endpoint_list_to_text(iterator):
    text_col_format = text_header_and_format(
        [(32, 'Owner'), (36, 'ID'), (None, 'Display Name')])

    for result in iterator:
        print(text_col_format.format(
            result['owner_string'], result['id'],
            display_name_or_cname(result)))


def assemble_generic_doc(datatype, *args, **kwargs):
    doc = {'DATA_TYPE': datatype}
    for argname in kwargs:
        if kwargs[argname] is not None:
            doc[argname] = kwargs[argname]
    return doc
