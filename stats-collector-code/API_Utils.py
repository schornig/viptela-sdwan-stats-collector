#!/usr/bin/env python3
import requests
import json
import logging
import sys

logging.addLevelName(25, "__INFO__")
logging.basicConfig(stream=sys.stdout,
                    format='%(asctime)s: %(module)s [%(funcName)s] [%(process)s] [%(levelname)s]: %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=25)

class CiscoException(Exception):
    pass

class ViptelaRestApiLib:
    def __init__(self, vmanage_ip, username, password):
        self.vmanage_ip = vmanage_ip
        self.headers = {'Content-Type': 'application/json'}
        self.session = requests.session()
        self.login(self.vmanage_ip, username, password)

    def login(self, vmanage_ip, username, password):
        """Login to vmanage"""
        base_url_str = 'https://{0}/'.format(vmanage_ip)
        login_str = 'j_security_check'
        token_str = 'dataservice/client/token'

        #Url for posting login data
        login_url = base_url_str + login_str
        token_url = base_url_str + token_str

        #Format data for loginForm
        login_data = {'j_username' : username, 'j_password' : password}

        #If the vmanage has a certificate signed by a trusted authority change verify to True
        login_response = self.session.post(url=login_url, data=login_data, verify=False)
        if b'<html>' in login_response.content or login_response.status_code != 200:
            raise CiscoException('Login Failed: {0}'.format(login_response.status_code))

        #If the vmanage has a certificate signed by a trusted authority change verify to True
        token_response = self.session.get(url=token_url, verify=False)
        if token_response.status_code == 200:
            self.headers['X-XSRF-TOKEN'] = token_response.content
        elif token_response.status_code == 404:
            pass
        else:
            raise CiscoException('Failed getting X-XSRF-TOKEN: {0}'.format(token_response.status_code))

    def get_request(self, mount_point):
        """GET request"""
        url = "https://%s/dataservice/%s"%(self.vmanage_ip, mount_point)

        response = self.session.get(url, headers=self.headers, verify=False)
        #response.raise_for_status()
        data = response.content

        return json.loads(data)

    def post_request(self, mount_point, payload):
        """POST request"""
        url = "https://%s/dataservice/%s"%(self.vmanage_ip, mount_point)

        dup_template_msg = "Template with name"
        dup_list_msg = "Duplicate policy list entry"
        dup_policy_msg = "Duplicate policy detected with name"
        dup_vedge_msg = "vEdge policy with name"
        dup_vsmart_msg = "vSmart policy with name"
        dup_token = "Umbrella Token entry already exists"
        version_msg = "Failed to create definition"
        unknown_msg = "Unknown error"

        payload = json.dumps(payload)
        self.headers['Content-Type'] = 'application/json'

        response = self.session.post(url=url, data=payload, headers=self.headers, verify=False)
        if response.status_code != 200:
            if (response.status_code == 400):
                response_details = str(response.json()['error']['details'])
                if  (response_details.startswith(dup_template_msg)) or \
                    (response_details.startswith(dup_list_msg)) or \
                    (response_details.startswith(dup_policy_msg)) or \
                    (response_details.startswith(dup_vedge_msg)) or \
                    (response_details.startswith(dup_vsmart_msg)) or \
                    (response_details.startswith(dup_token)) or \
                    (response_details.startswith(version_msg)) or \
                    (response_details.startswith(unknown_msg)):
                    return response_details
                else:
                    try:
                        print(response_details)
                    except:
                        print(response)
                    raise CiscoException("Fail - Post")
        try:
            data = response.json()
        except ValueError:
            data = "Successful"

        return data

    def put_request(self, mount_point, payload):
        """PUT request"""
        url = "https://%s/dataservice/%s"%(self.vmanage_ip, mount_point)

        payload = json.dumps(payload)
        self.headers['Content-Type'] = 'application/json'

        response = self.session.put(url=url, data=payload, headers=self.headers, verify=False)
        if response.status_code != 200:
                print(response.json()['error']['details'])
                raise CiscoException("Fail - Put")
        try:
            data = response.json()
        except ValueError:
            data = "Successful"

        return data

    def delete_request(self, mount_point):
        """DELETE request"""
        url = "https://%s/dataservice/%s"%(self.vmanage_ip, mount_point)
        factory_template_msg = "Template is a factory default"
        policy_list_ro_msg = "This policy list is a read only list and it cannot be deleted"
        policy_list_partner = "This policy list is created by a partner and can only be removed when the partner is deleted."

        response = self.session.delete(url=url, headers=self.headers, verify=False)

        data = response.content

        #print(response.status_code)
        if response.status_code != 200:
            if (response.status_code == 400):
                if (response.json()['error']['details'] == factory_template_msg):
                    return(response.json()['error']['details'])
                elif(response.json()['error']['details'] == policy_list_ro_msg):
                    return(response.json()['error']['details'])
                elif(response.json()['error']['details'] == policy_list_partner):
                    return(response.json()['error']['details'])
                else:
                    print(response.json()['error']['details'])
                    raise CiscoException("Fail - Delete")
            else:
                print(response)
                raise CiscoException("Fail - Delete")
        if data:
            return data
        else:
            return "Successful"

    def use_tenant(self, tenant):
        print("tenant")

        mount_point = "tenant"
        response = json.loads(sdwanp.get_request(mount_point))
        device_data = response["data"]
        tenant_id = ""
        for device in device_data:
            if device["name"] == tenant:
                tenant_id = device["tenantId"]
        if not tenant_id:
            raise CiscoException("Tenant {} not found! Please check tenant name and try again.".format(tenant))

        item = {}
        mount_point = "tenant/" + str(tenant_id) + "/switch"
        response = sdwanp.post_request(mount_point, item)

        self.headers["VSessionId"] = response["VSessionId"]