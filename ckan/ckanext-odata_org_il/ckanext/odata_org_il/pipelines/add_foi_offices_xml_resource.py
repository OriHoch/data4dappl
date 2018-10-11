from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
from collections import defaultdict
import logging, requests
from itertools import chain
from os import environ
import xml.etree.ElementTree as ET

FIELD_NAMES = ['Title', 'Published', 'MMDOfficesTypes', 'GovXDescription', 'ManagerName', 'Email', 'Fax',
               'ReceptionAddressNotes', 'ReceptionPhoneNumbers', 'websiteURL', 'PaymentBankTransfer',
               'GovXContentSection', 'FormEmail', 'FormFax', 'FormLetter', 'FormOnlineURL', 'forWizard', 'MMDSubjects',
               'MMDTypes', 'OfficeIcon', 'OfficeNameCode', 'OfficeTypeCode', 'PaymentCash', 'PaymentCheck',
               'PaymentOnlineURL', 'PaymentPhone', 'PaymentPostalBank', 'PaymentTreasury']


def get_foi_offices_xml_descriptor():
    return {'name': 'foi_offices_xml',
            'path': 'foi_offices_xml.csv',
            PROP_STREAMING: True,
            "schema": {
                "fields": [{'name': k, 'type': 'string'} for k in FIELD_NAMES]
            }}


def get_foi_offices_xml_resource(parameters, stats):
    filename = parameters.get('filename')
    if filename:
        root = ET.parse(filename).getroot()
    else:
        root = ET.fromstring(requests.get(parameters['url']).content)
    for node in root:
        row = {}
        unknown_tags = []
        for tag in node:
            if tag.tag in FIELD_NAMES:
                row[tag.tag] = tag.text
            else:
                unknown_tags.append(tag.tag)
        if len(unknown_tags) > 0:
            raise Exception('unknown tags: {}'.format(unknown_tags))
        else:
            yield row


def main():
    parameters, datapackage, resources, stats = ingest() + (defaultdict(int),)
    datapackage['resources'].append(get_foi_offices_xml_descriptor())
    spew(datapackage, chain(resources, [get_foi_offices_xml_resource(parameters, stats)]), stats)


if __name__ == '__main__':
    main()

