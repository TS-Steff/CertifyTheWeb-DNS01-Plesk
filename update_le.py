#!/usr/bin/env python3
# Copyright 1999-2016. Parallels IP Holdings GmbH. All Rights Reserved.
# https://github.com/plesk/api-examples/blob/master/python3/example.py

#import os
from plesk_api_client import PleskApiClient
import xml.etree.ElementTree as ET
import sys
import logging as log
from logging.handlers import TimedRotatingFileHandler

### USER VARIABLES ###
#host = os.getenv('REMOTE_HOST')
#login = os.getenv('REMOTE_LOGIN', 'admin')
#password = os.getenv('REMOTE_PASSWORD')

host = 'xxx'
login = 'xxx'
password = 'xxx'
log_filename = 'C:\\Service\\Scripts\\LE\\acme.log'

dns_record = ''
site_id = ''  #in plesk over over "Hosting Settings" / passed by Certify The Web
dns_value = ''

### Init other Variables ###
debug = False


def main(argv):

    
    log.basicConfig(
        handlers=[
            TimedRotatingFileHandler(
                filename=log_filename,
                #filemode='a',
                when='midnight',
                interval=1,
                backupCount=14,
                encoding='utf-8'
                )
        ],
        format='%(asctime)s %(levelname)s: %(message)s',
        level=log.INFO
    )


    log.info("---START---");
    if debug:
        log.debug("args: " + " ".join(sys.argv))
        log.debug(
        "If this script did anything it would create a TXT record called " + sys.argv[2]
        + " with the value " + sys.argv[3]
        + " you could optionally use the domain ("+sys.argv[1]+") "
        + " or zoneId ("+sys.argv[4]+") in your python script")
        
        
    dns_record = sys.argv[2] + '.'
    site_id = sys.argv[4]
    dns_value = sys.argv[3]
    
    client = PleskApiClient(host)
    client.set_credentials(login, password)
    log.info(f'Getting Records for Site: {site_id}')

    request = """
    <packet>
    <dns>
     <get_rec>
      <filter>
       <site-id>"""
    request += site_id
    request += """</site-id>
      </filter>
     </get_rec>
    </dns>
    </packet>
    """

    response = client.request(request)
    check_response(response)
    
    if debug: print(response)
    log.debug(response)
    
    root = ET.fromstring(response)
    
    dns_record_count = 0
    for result in root.findall('.//result'):
        host_element = result.find('.//host')
        host_value = result.find('.//value')
        host_type = result.find('.//type')
        host_id = result.find('.//id')
        
        if host_element.text == dns_record:
            dns_record_count += 1
            dns_record_id = host_id.text

    match dns_record_count:
        case 0:
            print('No records found. Adding record.')
            log.info('No records found. Going to add new record')
            dns_record_add(site_id, dns_value)
        case 1:
            print('Found 1 record. Going to delete id:', dns_record_id)
            log.info('Found 1 record. Going to delete record with id: ' + dns_record_id)
            dns_record_del(dns_record_id)
        case _:
            print('Something went wrong. Exiting!')
            print('Records found: ', dns_record_count)
            log.error('Something went terrebly wrong.')
            log.error('Records found: ' + dns_record_count)
            log.error('Exiting')
            exit()
                

def dns_record_del(record_id):
    print('delete record:', record_id)
    log.info(f'delete record:{record_id}')
    client = PleskApiClient(host)
    client.set_credentials(login, password)
    
    request = """
    <packet>
    <dns>
       <del_rec>
          <filter>
             <id>"""
    request += record_id
    request += """</id>
          </filter>
       </del_rec>
    </dns>
    </packet>
    """
    if debug:
        print('DEL REQUEST\n')
        print(request)
    log.debug(request)
        
    response = client.request(request)
    check_response(response)
    
    if debug: print(response)
    log.debug(response)

def dns_record_add(site_id, dns_value):
    print('adding new record')
    log.info(f'adding new record:{dns_value}')
    client = PleskApiClient(host)
    client.set_credentials(login, password)
    
    request = """
    <packet>
    <dns>
       <add_rec>
          <site-id>"""
    request += site_id
    request += """</site-id>
          <type>TXT</type>
          <host>_acme-challenge</host>
          <value>"""
    request += dns_value
    request += """</value>
       </add_rec>
    </dns>
    </packet>
    """
    if debug:
        print('ADD REQUEST\n')
        print(request)
        log.debug(request)
        
    response = client.request(request)
    check_response(response)
    if debug: print(response)
    log.debug(response)

def check_response(response):
    if debug:
        print('check_response')
        print(response)
    log.info('check_response')

    ### Testing Responses ###
    ## OK
    #response = '<?xml version="1.0" encoding="UTF-8"?><packet version="1.6.9.1"><dns><add_rec><result><status>ok</status><id>181442</id></result></add_rec></dns></packet>'

    ## err
    ##response = '<?xml version="1.0" encoding="UTF-8"?><packet version="1.6.9.1"><dns><add_rec><result><status>error</status><errcode>1007</errcode><errtext>DNS record \'_acme-challenge.test.domain. IN TXT MaqMBNDrHck8iI8dcymwBxk5y8kzeXAtOENGrBIlX6s\' already exists.</errtext></result></add_rec></dns></packet>'

    ## add
    #response = '<packet><dns><add_rec><site-id>5933</site-id><type>TXT</type><host>_acme-challenge</host><value>MaqMBNDrHck8iI8dcymwBxk5y8kzeXAtOENGrBIlX6s</value></add_rec></dns></packet>'

    root = ET.fromstring(response)

    # SYSTEEM MESSAGES
    for result in root.findall('.//system'):
        response_status = result.find('.//status')
        response_errcode = result.find('.//errcode')
        response_errtext = result.find('.//errtext')
        
        match response_status.text:
            case 'error':
                print('ERROR')
                if debug: print(response_errcode.text + ':', response_errtext.text)
                log.critical(f'Response error - Exiting\n' +
                                f'Status: {response_status.text}\n' + 
                                f'Code: {response_errcode.text}\n' +
                                f'Text: {response_errtext.text}')
                exit()

            case 'ok':
                if debug: print('Response OK')
                log.info('Response OK')

            case _:
                print('Something went wrong. - Response unknown - Exiting!')
                if debug: print(response_errcode.text + ':', response_errtext.text)
                log.critical(f'Response unknown - exiting\n' +
                                f'Status: {response_status.text}\n' + 
                                f'Code: {response_errcode.text}\n' +
                                f'Text: {response_errtext.text}')
                exit()

    # dns get_rec messages
    for result in root.findall('.//get_rec'):
        if debug: print("Response: GET_REC")
        log.info("Response: GET_REC")
        tmpStateOK = True
        
        for entry in result:
            if entry.find('.//status').text != 'ok': tmpStateOK = False
            if debug:
                print('ID: ' + entry.find('.//id').text + ' | ' +
                      'status: ' + entry.find('.//status').text + ' | ' +
                      'type: ' + entry.find('.//type').text + ' | ' +
                      'host: ' + entry.find('.//host').text + ' | ' +
                      'value: ' + entry.find('.//value').text)
            log.debug('ID: ' + entry.find('.//id').text)
            log.debug('status: ' + entry.find('.//status').text)
            log.debug('type: ' + entry.find('.//type').text)
            log.debug('host: ' + entry.find('.//host').text)
            log.debug('value: ' + entry.find('.//value').text)
        
        if tmpStateOK == False :
            log.critical('GET_REC ERROR\n', response)
            log.critical('EXITING')
            exit()
            
        
    # dns add_rec messages
    for result in root.findall('.//add_rec'):
        if debug: print('Response: ADD_REC')
        log.info('Response: ADD_REC')

        status = result.find('.//status').text

        match status:
            case 'ok':
                print('OK')
                if debug: print('Added new Entry with ID: ' + result.find('.//id').text)
                log.info('Added new Entry with ID: ' + result.find('.//id').text)                
            case 'error':
                print('ERROR')
                if debug:
                    print('Status not OK - ', result.find('.//status').text)
                    print('ErrCode: ', result.find('.//errcode').text)
                    print('ErrText: ', result.find('.//errtext').text)
                
                log.warning('Status not OK - ' + result.find('.//status').text)
                log.warning('ErrCode: ' + result.find('.//errcode').text)
                log.warning('ErrText: ' + result.find('.//errtext').text)                
            case _:
                print('ANY ELSE')
                if debug:
                    print('New entry details')
                    print('SiteID: ', result.find('.//site-id').text)
                    print('Type:   ', result.find('.//type').text)
                    print('Host:   ', result.find('.//host').text)
                    print('Value:  ', result.find('.//value').text)
                log.info('New entry details')
                log.info('SiteID: ' + result.find('.//site-id').text)
                log.info('Type:   ' + result.find('.//type').text)
                log.info('Host:   ' + result.find('.//host').text)
                log.info('Value:  ' + result.find('.//value').text)                


    # dns del_rec messages
    for result in root.findall('.//del_rec'):
        if debug: print("Response: DEL_REC")
        log.info("Response: DEL_REC")
        
if __name__ == '__main__':
    main(sys.argv)
