import xml.etree.cElementTree as ET
from collections import Counter, defaultdict
import re
import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)
###
#Notes
# count children of elements, percentages

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
users = Counter()
sources = Counter()
attributions = Counter()
timestamps = Counter()
tag_parents = set()

class Entity:
    def __init__(self):
        self.tag = None
        self.count = 0
        self.attributes = defaultdict(Counter)
        self.children = []

attrs = defaultdict(Entity)

def entity_audit(elem, auditor):
    if elem.tag not in auditor:
        auditor[elem.tag] = {   'text_sample': elem.text,
                                'count': 0,
                                'children': Counter(),
                                'attribute_count': Counter(),
                                'attribute_sample': dict() }
    auditor[elem.tag]['count'] += 1
    for child in list(elem):
        auditor[elem.tag]['children'][child.tag] += 1
    for attr in elem.attrib:
        auditor[elem.tag]['attribute_count'][attr] += 1
        auditor[elem.tag]['attribute_sample'][attr] = elem.attrib[attr]
    return auditor


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type] += 1

def audit_user(elem):
    user = elem.attrib['user']
    users[user] += 1

def audit_source(elem):
    key = elem.attrib['k']
    if key == 'source':
        sources[elem.attrib['v']] += 1
    elif key == 'attribution':
        attributions[elem.attrib['v']] += 1

def audit_timestamp(elem):
    ts = elem.attrib['timestamp']
    dt = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
    timestamps[dt.strftime('%Y-%m')] += 1

def audit(osmfile):
    osm_file = open(osmfile, "r")
    element_count = Counter()
    tag_vals = {}
    auditor = {}
    tag_type = Counter()
    for event, elem in ET.iterparse(osm_file, events=('end',)):        
        element_count[elem.tag] += 1
        if elem.tag not in tag_vals:
            # tag_vals[elem.tag] = defaultdict(set)
            tag_vals[elem.tag] = Counter()
        auditor = entity_audit(elem, auditor)
        for tag in elem.iter("tag"):
            tag_vals[elem.tag][tag.attrib['k']] += 1
            if tag.attrib['k'] == 'type':
                tag_type[tag.attrib['v']] += 1
        # if elem.findall('tag'):
        #     tag_parents.add(elem.tag)

        # tags[elem.tag] += 1
        # for attr in elem.attrib:
        #     attrs[elem.tag][attr] += 1
        # if elem.tag == "node" or elem.tag == "way":
        #     # audit_user(elem)
        #     audit_timestamp(elem)
            # for tag in elem.iter("tag"):
            #     audit_source(tag)
            #     if is_street_name(tag):
            #         audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    for a in auditor:
        auditor[a]['children'] = dict(auditor[a]['children'])
        auditor[a]['attribute_count'] = dict(auditor[a]['attribute_count'])
    for t in tag_vals:
        tag_vals[t] = dict(tag_vals[t])
    pp.pprint(dict(element_count))
    pp.pprint(auditor)
    pp.pprint(dict(tag_type))
    pp.pprint(tag_vals.keys())
    for t in tag_vals:
        for k in tag_vals[t].keys():
            if ":" in k:
                print k
    return

if __name__ == "__main__":
    out = audit('data/providence_et_al.xml')
    # print tags.most_common(100)
    # for tag in out:
    #     print tag
    #     print out[tag]
    pp.pprint(out)
    # x = users.most_common(100)
    # print x
	# for k,v in users.items():
	# 	print k, v