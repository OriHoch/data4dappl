import re
from datapackage_pipelines.wrapper import process


def modify_datapackage(datapackage, parameters, stats):
    assert datapackage['resources'][0]['name'] == 'foi_offices_xml'
    datapackage['resources'][0]['schema']['fields'].append({
        'name': 'normalized_title',
        'type': 'string'
    })
    datapackage['resources'][0]['schema']['fields'].append({
        'name': 'mmdOfficesTypes_tid',
        'type': 'number'
    })
    return datapackage


def process_row(row, row_index, resource_descriptor, resource_index, parameters, stats):
    assert resource_index == 0
    row['normalized_title'] = '{}: {}'.format(re.sub(' +', ' ', row['MMDOfficesTypes']).strip(), re.sub(' +', ' ', row['Title']).strip())
    row['mmdOfficesTypes_tid'] = {
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
    }[re.sub(' +', ' ', row['MMDOfficesTypes']).strip()]
    return row


process(modify_datapackage=modify_datapackage, process_row=process_row)
