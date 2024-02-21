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
logging = True
debug = True


def main(argv):


    if logging:
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

    if logging:
        log.info("---START---");
        if debug:
            log.info("args: " + " ".join(sys.argv))
            log.info(
            "If this script did anything it would create a TXT record called " + sys.argv[2]
            + " with the value " + sys.argv[3]
            + " you could optionally use the domain ("+sys.argv[1]+") "
            + " or zoneId ("+sys.argv[4]+") in your python script")
        
        
    dns_record = sys.argv[2]
    site_id = sys.argv[4]
    dns_value = sys.argv[3]
    
    client = PleskApiClient(host)
    client.set_credentials(login, password)

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
    if debug:
        print(response)
        log.info(response)
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
            dns_record_add(site_id, dns_value)
        case 1:
            print('Found 1 record. Going to delete id:', dns_record_id)
            dns_record_del(dns_record_id)
        case _:
            print('Something went wrong. Exiting!')
            exit()
                

def dns_record_del(record_id):
    print('delete record:', record_id)
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
        log.info(request)
        
    response = client.request(request)
    if debug:
        print(response)
        log.info(response)

def dns_record_add(site_id, dns_value):
    print('adding new record')
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
        log.info(request)
        
    response = client.request(request)
    if debug:
        print(response)
        log.info(response)

if __name__ == '__main__':
    main(sys.argv)



