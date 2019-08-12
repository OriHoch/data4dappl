import logging, re
from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew


def is_title_type_match(xml_normalized_title, group_normalized_title):
    if xml_normalized_title == group_normalized_title:
        return True
    else:
        xml_split_title = xml_normalized_title.split(':')
        if xml_split_title[0].strip() in {
            "איגוד ערים": 374,
            "אחר": 57,
            "ועדת תכנון מרחבית": 373,
            "תאגיד סטטוטורי": 49,
            "חברה עירונית": 325,
            "ועדים מקומיים": 371,
            "רשות מקומית": 60,
            "משרד ממשלתי": 57,
            "חברה ממשלתית": 47,
            "יחידת סמך": 58,
            "מוסד ממלכתי": 56,
            "מועצה דתית": 88,
            "השכלה גבוהה": 281,
            "התאחדות ספורט": 326,
            "קופת חולים": 89,
        } and ':'.join(xml_split_title[1:]).strip() == group_normalized_title:
            return True
        else:
            return False


def get_resources(resources):
    xml_entities = []
    existing_entities = []

    def get_xml_resource(xml_resource):
        for row in xml_resource:
            xml_entities.append(row)
            yield row

    def get_existing_entities_resource(existing_entities_resource):
        for row in existing_entities_resource:
            existing_entities.append(row)
            yield row

    def get_matching_entities_resource():
        matched_xml_rownums_to_existing_rownums = {}
        for xml_rownum, xml_row in enumerate(xml_entities):
            xml_normalized_title = xml_row['normalized_title']
            for existing_rownum, existing_row in enumerate(existing_entities):
                existing_normalized_title = re.sub(' +', ' ', existing_row['title']).strip()
                if is_title_type_match(xml_normalized_title, existing_normalized_title):
                    matched_xml_rownums_to_existing_rownums.setdefault(xml_rownum, []).append(existing_rownum)
        logging.info('{} xml rows matched to existing groups based on title'.format(len(matched_xml_rownums_to_existing_rownums)))
        for xml_rownum, xml_row in enumerate(xml_entities):
            if xml_rownum not in matched_xml_rownums_to_existing_rownums:
                yield {
                    'title': xml_row['normalized_title'],
                    'group_id': '',
                    'group_name': '',
                    'email': xml_row['Email'],
                    'officenamecode': xml_row['OfficeNameCode'],
                    'mmdOfficesTypes_tid': xml_row['mmdOfficesTypes_tid'],
                }
        skip_existing_rownums = []
        for xml_rownum, matched_existing_rownums in matched_xml_rownums_to_existing_rownums.items():
            if len(matched_existing_rownums) != 1:
                raise Exception('xml_rownum {} has {} matching existing rownums: {}'.format(
                    xml_rownum, len(matched_existing_rownums), matched_existing_rownums))
            matched_existing_rownum = matched_existing_rownums[0]
            skip_existing_rownums.append(matched_existing_rownum)
            xml_row = xml_entities[xml_rownum]
            existing_row = existing_entities[matched_existing_rownum]
            yield {
                'title': existing_row['title'],
                'group_id': existing_row['group_id'],
                'group_name': existing_row['group_name'],
                'email': xml_row['Email'],
                'officenamecode': xml_row['OfficeNameCode'],
                'mmdOfficesTypes_tid': xml_row['mmdOfficesTypes_tid'],
            }
        for existing_rownum, existing_row in enumerate(existing_entities):
            if existing_rownum not in skip_existing_rownums:
                email, officenamecode, tid = None, None, None
                for extra in existing_row['group']['extras']:
                    if extra['key'] == 'email':
                        email = extra['value']
                    elif extra['key'] == 'officenamecode':
                        officenamecode = extra['value']
                    elif extra['key'] == 'mmdOfficesTypes_tid':
                        tid = extra['value']
                yield {
                    'title': existing_row['title'],
                    'group_id': existing_row['group_id'],
                    'group_name': existing_row['group_name'],
                    'email': email,
                    'officenamecode': officenamecode,
                    'mmdOfficesTypes_tid': tid,
                }

    def normalize_titles(resource):
        for row in resource:
            split_title = row['title'].split(':')
            if split_title[0].strip() in {
                "איגוד ערים": 374,
                "אחר": 57,
                "ועדת תכנון מרחבית": 373,
                "תאגיד סטטוטורי": 49,
                "חברה עירונית": 325,
                "ועדים מקומיים": 371,
                "רשות מקומית": 60,
                "משרד ממשלתי": 57,
                "חברה ממשלתית": 47,
                "יחידת סמך": 58,
                "מוסד ממלכתי": 56,
                "מועצה דתית": 88,
                "השכלה גבוהה": 281,
                "התאחדות ספורט": 326,
                "קופת חולים": 89,
            }:
                row['original_title'] = row['title']
                row['title'] = ':'.join(split_title[1:]).strip()
                row['type_title'] = split_title[0].strip()
            else:
                row['original_title'] = row['title']
                row['title'] = row['title'].strip()
                row['type_title'] = ''
            yield row

    yield get_xml_resource(next(resources))
    yield get_existing_entities_resource(next(resources))
    yield normalize_titles(get_matching_entities_resource())


def main():
    parameters, datapackage, resources = ingest()
    datapackage['resources'].append({
        'name': 'match_foi_offices_xml_existing_entities',
        'path': 'match_foi_offices_xml_existing_entities.csv',
        PROP_STREAMING: True,
        'schema': {
            'fields': [
                {'name': 'original_title', 'type': 'string'},
                {'name': 'type_title', 'type': 'string'},
                {'name': 'title', 'type': 'string'},
                {'name': 'group_id', 'type': 'string'},
                {'name': 'group_name', 'type': 'string'},
                {'name': 'email', 'type': 'string'},
                {'name': 'officenamecode', 'type': 'string'},
                {'name': 'mmdOfficesTypes_tid', 'type': 'number'}
            ]
        }
    })
    spew(datapackage, get_resources(resources), {})


if __name__ == '__main__':
    main()
