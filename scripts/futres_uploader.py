#!/usr/bin/python

import argparse
import json
import sys
from os import listdir, path
from os.path import isfile, join

import requests


ENDPOINT = 'https://api.geome-db.org/'

CSV_FILE = "{}.csv"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}



def upload_files(project_id, access_token, filename, code, accept_warnings=False, attempt_upload=False):   
    create_expedition(project_id, code, access_token)
    upload_data(project_id, code, access_token, filename, accept_warnings, attempt_upload)


def create_expedition(project_id, code, access_token):
    print('\n\nAttempting to create expedition: ', code)

    url = "{}projects/{}/expeditions/{}?access_token={}".format(
        ENDPOINT, project_id, code, access_token)
    expedition = {
        'expeditionTitle': code,
        'expeditionCode': code,
        'visibility': 'anyone',
        'public': True,
        'metadata': {},
    }
    response = requests.post(url, json=expedition, headers=headers)

    if response.status_code == 400 and response.json().get('usrMessage').find('already exists.') > -1:
        print("Expedition \"{}\" already exists".format(code))
    elif response.status_code > 400:
        print('\nERROR: ' + response.json().get('usrMessage'))
        print('\n')
        response.raise_for_status()
    elif response.status_code == 400:
        print('\nERROR: ' + response.json().get('usrMessage'))
        print('\n')
        response.raise_for_status()
    else:
        print('Successfully created expedition: ', code)


def upload_data(project_id, code, access_token, filename, accept_warnings, attempt_upload):
    print('Validating data for expedition: ', code)

    validate_url = "{}data/validate?access_token={}".format(
        ENDPOINT, access_token)

    data = {
        'projectId': project_id,
        'expeditionCode': code,
        'upload': True,
        'reloadWorkbooks': True,
    }

    metadata = [
        {
            "dataType": 'TABULAR',
            "filename": filename,
            "reload": True,
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
            print('\nERROR: ' + r.json().get('usrMessage'))
        except ValueError:
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
                print('\t\tBAD ENCODING, TRY AGAIN: ' +
                      message.get('message').encode('cp1252'))

        print('\n')

    if 'messages' in response:
        for entityResults in response.get('messages'):
            if len(entityResults.get('errors')) > 0:
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

    if (attempt_upload):
        if response.get('hasError'):
            print("Validation error(s) attempting to upload expedition: {}".format(code))
            sys.exit()
        elif not response.get('isValid') and not accept_warnings:
            cont = input(
                "Warnings found during validation. Would you like to continue? (y/n)   ")
            if cont.lower() != 'y':
                sys.exit()

        upload_url = response.get('uploadUrl') + '?access_token=' + access_token
        r = requests.put(upload_url, headers=headers)
        if r.status_code > 400:
            print('\nERROR: ' + r.json().get('usrMessage'))
            print('\n')
            r.raise_for_status()

        if(str(r.json().get('usrMessage')) == "None"):
            print('Successfully uploaded expedition: ', code)
        else:    
            print(str(r.json().get('usrMessage')))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Upload a futres files. '
                    'We will create an expedition if necessary. We expect 1 files for each expedition. ')
    parser.add_argument(
        "project_id", help="The id of the project we're uploading")
    parser.add_argument(
        "access_token", help="Access Token of the user to upload under")
    parser.add_argument("filename",
                        help="Name of file")
    parser.add_argument("expedition",
                        help="Expedition to upload")    
    parser.add_argument("attempt_upload",
                        help="Default to False for attempt_upload")                          
    parser.add_argument(
        "--accept_warnings", help="Continue to upload any data with validation warnings", default=False)
    
    #args = parser.parse_args()
    #upload_files(args.project_id, args.file, args.expedition, args.accept_warnings)
    
    access_token = "foo"
    filename = "test.csv"
    project_id = 232
    expedition = "test3"
    accept_warnings = False
    attempt_upload = False
    
    upload_files(232,access_token,filename,expedition,accept_warnings, attempt_upload)
