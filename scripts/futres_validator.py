#!/usr/bin/python

import argparse
import json
import sys
from os import listdir, path
from os.path import isfile, join

import requests


ENDPOINT = 'https://api.geome-db.org/'

CSV_FILE = "{}.xlsx"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}



def upload_files(project_id, filename, code):   
    validate_data(project_id, filename, code)


def validate_data(project_id, filename, code):
    errorsFound = False
    # use the test expedition for data validation
    print('Validating data for filename: ', filename)


    validate_url = "{}data/validate".format(
        ENDPOINT)
    data = {
        'projectId': project_id,
        'expeditionCode': code,
        'upload': False,
        'reloadWorkbooks': False,
    }

    metadata = [
        {
            "dataType": 'TABULAR',
            "filename": filename,
            "reload": False,
            "metadata": {
                "sheetName": "Samples"
            }

        }
    ]

    files = [
        ('dataSourceFiles', (filename, open(filename, 'rb'), 'text/plain')),
        ('dataSourceMetadata', (None, json.dumps(metadata), 'application/json'))
    ]

    h = dict(headers)
    h['Content-Type'] = None
    r = requests.post(validate_url, data=data, files=files, headers=h)
    if r.status_code >= 400:
        try:
            errorsFound = True
            print('\nERROR: ' + r.json().get('usrMessage'))
        except ValueError:
            errorsFound = True
            print('\nERROR: ' + r.text)
    print('\n')
    r.raise_for_status()

    response = r.json()

    def print_messages(groupMessage, messages):
        print("\t{}:\n".format(groupMessage))

        for message in messages:
            try:
                print("\t\t" + message.get('message'))
            except ValueError:
                errorsFound = True
                print('\t\tBAD ENCODING, TRY AGAIN: ' +
                      message.get('message').encode('cp1252'))

        print('\n')

    if 'messages' in response:
        for entityResults in response.get('messages'):
            if len(entityResults.get('errors')) > 0:
                errorsFound = True
                print("\n\n{} found on worksheet: \"{}\" for entity: \"{}\"\n\n".format('Errors', entityResults.get('sheetName'),
                                                                                        entityResults.get('entity')))

                for group in entityResults.get('errors'):
                    print_messages(group.get('groupMessage'),
                                   group.get('messages'))

            if len(entityResults.get('warnings')) > 0:
                print("\n\n{} found on worksheet: \"{}\" for entity: \"{}\"\n\n".format('Warnings', entityResults.get('sheetName'),
                                                                                        entityResults.get('entity')))

                for group in entityResults.get('warnings'):
                    print_messages(group.get('groupMessage'),
                                   group.get('messages'))

    if (errorsFound):
        print ("ERRORS ON DATASET")
        sys.exit(1)
    else:
        print ("DATASET GOOD TO GO! (May want to fix Warnings)")
        sys.exit(0)
        
if __name__ == "__main__":

    # Default futres project is 232.. This is a public FuTRES project which we can use to test against.
    project_id = 232
    # Default expedition to test against is 'test'... we don't actually load data to the test expedition
    # but use it here since we need some expedition.
    expedition_code = 'test'

    parser = argparse.ArgumentParser(
        description='Upload a futres files. '
                    'We will create an expedition if necessary. We expect 1 files for each expedition. ')
    parser.add_argument("filename",
                        help="Name of file")
    

    args = parser.parse_args()
    upload_files(232, args.filename, expedition_code)
    
    #upload_files(232,"test.csv")
