# -*- coding: utf-8 -*-
import csv
import datetime
import json
import os,ssl
import urllib.request


import elasticsearch.helpers
from elasticsearch import Elasticsearch, RequestsHttpConnection, serializer, compat, exceptions

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


TYPE = 'record'


# see https://github.com/elastic/elasticsearch-py/issues/374
class JSONSerializerPython2(serializer.JSONSerializer):
    """Override elasticsearch library serializer to ensure it encodes utf characters during json dump.
    See original at: https://github.com/elastic/elasticsearch-py/blob/master/elasticsearch/serializer.py#L42
    A description of how ensure_ascii encodes unicode characters to ensure they can be sent across the wire
    as ascii can be found here: https://docs.python.org/2/library/json.html#basic-usage
    """

    def dumps(self, data):
        # don't serialize strings
        if isinstance(data, compat.string_types):
            return data
        try:
            return json.dumps(data, default=self.default, ensure_ascii=True)
        except (ValueError, TypeError) as e:
            raise exceptions.SerializationError(data, e)


class ESLoader(object):
    def __init__(self, data_dir, index_name, drop_existing=False, alias=None, host='localhost:9200'):
        """
        :param data_dir
        :param index_name: the es index to upload to
        :param drop_existing:
        :param alias: the es alias to associate the index with
        """
        self.data_dir = data_dir
        self.index_name = index_name
        self.drop_existing = drop_existing
        self.alias = alias
        self.es = Elasticsearch([host], serializer=JSONSerializerPython2())

        # Create lookup file for mapping trait URIs to trait Labels
        self.lookup = dict()
        with urllib.request.urlopen("https://plantphenology.org//futresapi/v2/fovt/") as url:
            data = json.loads(url.read().decode())
            for trait in data:
                self.lookup[trait['termID']] = trait['label']

        # Create loookup file for mapping projectIDs to projectTitles
        self.lookup_project = dict()
        with urllib.request.urlopen("https://raw.githubusercontent.com/futres/fovt-data-pipeline/master/data/projects.json") as url:
            data = json.loads(url.read().decode())
            for project in data:
                self.lookup_project[project['projectID']] = project['projectTitle'].replace('_',' ')

    def load(self):
        if not self.es.indices.exists(self.index_name):
            print ('creating index ' + self.index_name)
            self.__create_index()
        elif self.drop_existing:
            print('deleting index ' + self.index_name)
            self.es.indices.delete(index=self.index_name)
            print ('creating index ' + self.index_name)
            self.__create_index()
        
        print('indexing ' + self.data_dir)
        
        doc_count = 0

        for file in get_files(self.data_dir):
            try:
                doc_count += self.__load_file(file)
            except RuntimeError as e:
                print(e)
                print("Failed to load file {}".format(file))

        print("Indexed {} documents total".format(doc_count))

    def __load_file(self, file):
        doc_count = 0
        data = []

        with open(file) as f:
            print("Starting indexing on " + f.name)
            reader = csv.DictReader(f)

            for row in reader:
                # split delimited traits into an array so es_loader handles it properly
                row['traits'] = row['traits'].split("|")

                # mapped traits are just those traits we care about listing for the interface
                # and mapped to rdfs:label using lookup table
                mapped_traits = []
                for trait in row['traits']:
                    try:
                        mapped_traits.append(self.lookup[trait])
                    except:
                        pass
                row['mapped_traits'] = mapped_traits

                # A mapping of projects to use instead of IDs
                row['mapped_project'] = self.lookup_project[row['projectID']]

                # remove hashes from measurementType
                row['measurementType'] = row['measurementType'].replace('{', '').replace('}','')

                # gracefully handle empty locations
                if (row['decimalLatitude'] == '' or row['decimalLongitude'] == ''): 
                    row['location'] = ''
                else:
                    row['location'] = row['decimalLatitude'] + "," + row['decimalLongitude'] 

                # pipeline code identifies null yearCollected values as 'unknown'. es_loader should be empty string
                if (row['yearCollected'] == 'unknown'): 
                    row['yearCollected'] = ''

                if (row['lifeStage'] == ''): 
                    row['lifeStage'] == 'Unknown' 
                if (row['family'] == ''): 
                    row['family'] == 'Unknown' 
                if (row['order'] == ''): 
                    row['order'] == 'Unknown' 
                if (row['class'] == ''): 
                    row['class'] == 'Unknown' 

                data.append({k: v for k, v in row.items() if v})  # remove any empty values

            elasticsearch.helpers.bulk(client=self.es, index=self.index_name, actions=data, 
                                       raise_on_error=True, chunk_size=10000, request_timeout=60)
            doc_count += len(data)
            print("Indexed {} documents in {}".format(doc_count, f.name))

        return doc_count

    def __create_index(self):
        request_body = {
            "mappings": {
                    "properties": {
                        "mapped_traits": {"type": "keyword"},
                        "lifeStage": {"type": "keyword"},
                        "genus": {"type": "keyword"},
                        "family": {"type": "keyword"},
                        "order": {"type": "keyword"},
                        "class": {"type": "keyword"},
                        "projectID": {"type": "keyword"},
                        "mapped_project": {"type": "keyword"},
                        "basisOfRecord": {"type": "keyword"},
                        "country": {"type": "keyword"},
                        "sex": {"type": "keyword"},
                        "yearCollected": {"type": "integer"},
                        "measurementType": {"type": "text"},
                        "measurementValue": {"type": "float"},
                        "decimalLatitude": { "type": "float" },
                        "decimalLongitude": { "type": "float" },
                        "minimumChronometricAge": { "type": "float" },
                        "maximumChronometricAge": { "type": "float" },
                        "minimumChronometricAgeReferenceSystem": { "type": "keyword" },
                        "maximumChronometricAgeReferenceSystem": { "type": "keyword" },
                        "location": { "type": "geo_point" }                        
                    }
            }
        }
        self.es.indices.create(index=self.index_name, body=request_body)
        
def get_files(dir, ext='csv'):
    for root, dirs, files in os.walk(dir):

        if len(files) == 0:
            print("no files found in {}".format(dir))

        for file in files:
            if file.endswith(ext):
                yield os.path.join(root, file)    

index = 'futres'
drop_existing = True
alias = 'futres'
host =  'tarly.cyverse.org:80'
#data_dir = 'data/output/output_reasoned_csv/'
data_dir = '/home/jdeck/data/futres/data/output/output_reasoned_csv/'

loader = ESLoader(data_dir, index, drop_existing, alias, host)
loader.load()


