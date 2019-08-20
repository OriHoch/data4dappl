import logging, re
from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
import requests
from os import environ


CKAN_API_KEY = environ.get('CKAN_API_KEY')
CKAN_URL = environ.get('CKAN_URL')
assert CKAN_API_KEY and CKAN_URL
CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}


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


def get_resources(resources, parameters):
    update_groups = parameters['update-groups']

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

    groups_matching_foi_entities = []

    def get_groups_matching_foi_entities(resource):
        for row in resource:
            groups_matching_foi_entities.append(row)
            yield row

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
    yield get_groups_matching_foi_entities(next(resources))
    yield normalize_titles(get_matching_entities_resource())

    def get_group_actions():
        updated_titles = []
        # implementation of this algorithm: https://github.com/OriHoch/data4dappl/issues/98#issuecomment-522880324
        # first iteration over all rows:
        for row in groups_matching_foi_entities:
            # for each row which have non-empty FOI match original_title
            if row['FOI match original_title'] and row['FOI match original_title'].strip() != "":
                # update the group specified in the row's group_id
                # update/add data from the xml item matching the FOI match original_title
                group_id = row['group_id']
                normalized_title = row['FOI match original_title'].strip()
                updated_titles.append(normalized_title)
                matching_xml_rows = [xml_row for xml_row in xml_entities
                                     if xml_row['normalized_title'].strip() == normalized_title]
                if len(matching_xml_rows) != 1:
                    matching_xml_rows = [xml_row for xml_row in xml_entities
                                         if ":".join(xml_row['normalized_title'].split(":")[1:]).strip() == normalized_title]
                assert len(matching_xml_rows) == 1, "Invalid matching rows for title {} : {}".format(normalized_title, matching_xml_rows)
                xml_row = matching_xml_rows[0]
                yield {
                    'action': 'update existing group',
                    'group_id': group_id,
                    **{k: str(v) for k, v in xml_row.items() if k in ["Title", "MMDOfficesTypes", "ManagerName",
                                                                      "Email", "mmdOfficesTypes_tid",
                                                                      "OfficeNameCode", "OfficeTypeCode"]},
                    "xml_row": xml_row,
                }
        # second iteration over all rows:
        for row in groups_matching_foi_entities:
            # for each row which have empty group_id
            if not row['group_id'] or row['group_id'].strip() == "":
                # for each row which original_title was not updated in first iteration:
                if len([True for title in updated_titles if title in row['original_title']]) == 0:
                    # add a new group from the xml item matching the original_title
                    matching_xml_rows = [xml_row for xml_row in xml_entities if xml_row['normalized_title'].strip() == row['original_title']]
                    if len(matching_xml_rows) != 1:
                        matching_xml_rows = [xml_row for xml_row in xml_entities
                                             if ":".join(xml_row['normalized_title'].split(":")[1:]).strip() == row['original_title']]
                    assert len(matching_xml_rows) == 1, "Invalid matching rows for title {} : {}".format(row['original_title'], matching_xml_rows)
                    xml_row = matching_xml_rows[0]
                    yield {
                        'action': 'add new group',
                        'group_id': "",
                        **{k: str(v) for k, v in xml_row.items() if k in ["Title", "MMDOfficesTypes", "ManagerName",
                                                                          "Email", "mmdOfficesTypes_tid",
                                                                          "OfficeNameCode", "OfficeTypeCode"]},
                        "xml_row": xml_row,
                    }

    def run_update_groups(group_actions):
        session = requests.session()
        session.headers.update(CKAN_AUTH_HEADERS)
        for row_num, row in enumerate(group_actions):
            yield {k: v for k, v in row.items() if k != "xml_row"}
            if update_groups and row["action"] == "add new group":
                xml_row = row["xml_row"]
                entity_id = "foi-201908-{}".format(row_num)
                title = xml_row['Title']
                logging.info('Creating group name = {} with title = {}'.format(entity_id, title))
                extras = [{'key': k, 'value': v} for k, v in xml_row.items() if k not in [
                    "normalized_title", "Email", "Title", "OfficeNameCode"
                ]]
                extras.append({"key": "email", "value": xml_row["Email"]})
                extras.append({"key": "officenamecode", "value": xml_row["OfficeNameCode"]})
                # logging.info(extras)
                if entity_id in ["foi-201908-756", "foi-201908-755"]: continue
                group_update_res = session.post('{}/api/3/action/group_create'.format(CKAN_URL),
                                                json=dict(name=entity_id, title=title,
                                                          state='active', extras=extras)).json()
                assert group_update_res and group_update_res.get('success'), str(group_update_res)

    yield run_update_groups(get_group_actions())


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
    datapackage['resources'].append({
        'name': 'group_actions',
        'path': 'group_actions.csv',
        PROP_STREAMING: True,
        'schema': {
            'fields': [
                {"name": "action", "type": "string"},
                {"name": "group_id", "type": "string"},
                {'name': 'Title', 'type': 'string'},
                {'name': 'MMDOfficesTypes', 'type': 'string'},
                {'name': 'ManagerName', 'type': 'string'},
                {'name': 'Email', 'type': 'string'},
                {'name': 'mmdOfficesTypes_tid', 'type': 'string'},
                {'name': 'OfficeNameCode', 'type': 'string'},
                {'name': 'OfficeTypeCode', 'type': 'string'},
            ]
        }
    })
    spew(datapackage, get_resources(resources, parameters), {})


if __name__ == '__main__':
    main()
