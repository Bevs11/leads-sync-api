import requests
import os
import json
from fastapi import HTTPException
from typing import List

HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
HUBSPOT_BASE_URL = os.getenv("HUBSPOT_BASE_URL", "https://api.hubapi.com")

class HubspotAPI:
    """
    Everything about the Hubspot API.
    """
    def __init__(self):
        self.access_token = HUBSPOT_ACCESS_TOKEN
        self.base_url = HUBSPOT_BASE_URL

    def get_contacts(self):
        url = f"{self.base_url}/crm/v3/objects/contacts"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def create_contact(self, contact_data):
        url = f"{self.base_url}/crm/v3/objects/contacts"
        payload = {
            "properties": {
                "firstname": contact_data.firstname,
                "lastname": contact_data.lastname,
                "email": contact_data.email,
                "phone": contact_data.phone,
                "company": contact_data.company
            }
        }
    
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        print("payload", payload)
        print("url", url)
        print("headers", headers)
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise HTTPException(status_code = 400, details=str(e))

    def chunk_data(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    def batch_sync_contacts(self, contacts:List, batch_size:int=100):
        """
        response sample:
        {
            "data": [    {
                "id": "208130974412",
                "properties": {
                    "createdate": "2025-08-15T00:09:31.209Z",
                    "email": "four@mail.com",
                    "hs_is_unworked": "true",
                    "hs_object_id": "208130974412",
                    "hs_object_source": "INTEGRATION",
                    "hs_object_source_id": "17895116",
                    "hs_object_source_label": "INTEGRATION",
                    "hs_pipeline": "contacts-lifecycle-pipeline",
                    "lastmodifieddate": "2025-08-15T00:09:48.897Z",
                    "lifecyclestage": "lead"
                },
                "createdAt": "2025-08-15T00:09:31.209Z",
                "updatedAt": "2025-08-15T00:09:48.897Z",
                "archived": false,
                "new": false
            }],
            "created_contacts": 0,
            "updated_contacts": 1
        }
        """
        url = f"{self.base_url}/crm/v3/objects/contacts/batch/upsert"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        print("contacts", contacts)
        print("url", url)
        print("headers", headers)

        response_json = []
        created_contacts = 0
        updated_contacts = 0

        for chunked_data in self.chunk_data(contacts, batch_size):
            payload = {
                "inputs": [
                    {
                        "properties": {
                            "firstname": contact.firstname,
                            "lastname": contact.lastname,
                            "email": contact.email,
                            "phone": contact.phone,
                            "company": contact.company
                        },
                        "id": contact.email,
                        "idProperty": "email"
                    }
                    for contact in chunked_data
                ]
            }
            print("payload", json.dumps(payload, indent=2))

            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=600)
            print("Status code:", response.status_code)
            print("Response text:", response.text)

            try:
                response_json.extend(response.json()['results'])
            except ValueError:
                raise HTTPException(status_code=400, detail="HubSpot returned non-JSON response")
        
        for result in response_json:
            if result.get('new') == True:
                created_contacts += 1
            elif result.get('new') == False:
                updated_contacts += 1

        return {
            "data": response_json,
            "created_contacts": created_contacts,
            "updated_contacts": updated_contacts
        }