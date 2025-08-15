import requests
import os
import json
from fastapi import HTTPException
from typing import List
from app.crud import check_for_duplicates, check_for_empty_fields, check_for_email_validity


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
        """
        Creates a new contact in HubSpot CRM using the provided contact data.

        Args:
            contact_data: An object containing contact details (firstname, lastname, email, phone, company).

        Returns:
            dict: The JSON response from the HubSpot API.

        Raises:
            HTTPException: If the HubSpot API returns an HTTP error.
        """
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
        Batch syncs a list of contacts with HubSpot using the batch upsert endpoint.

        - Validates contacts for empty fields, invalid emails, and duplicates.
        - Splits contacts into batches of size `batch_size`.
        - Sends each batch to HubSpot for upsert (create or update).
        - Tracks and returns counts of created, updated, and errored contacts.
        - Collects details of errors and responses for reporting.

        Args:
            contacts (List): List of contact objects to sync.
            batch_size (int, optional): Number of contacts per batch. Defaults to 100.

        Returns:
            dict: Summary of sync results including counts, details, and errors.
        """
        url = f"{self.base_url}/crm/v3/objects/contacts/batch/upsert"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        response_json = []
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = {}
        
        valid_list, empty_email = check_for_empty_fields(contacts)
        valid_list, invalid_email = check_for_email_validity(valid_list)
        valid_list, duplicates = check_for_duplicates(valid_list)

        def add_errors(key, items):
            nonlocal error_count
            if items:
                error_count += len(items)
                errors[key] = [item.model_dump() for item in items]

        add_errors('duplicates', duplicates)
        add_errors('empty_email', empty_email)
        add_errors('invalid_email', invalid_email)
            

        for chunked_data in self.chunk_data(valid_list, batch_size):
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


            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=600)

            data = response.json()

            if data.get("results"):
                response_json.extend(data["results"])
            else:
                error_count += len(chunked_data)
                errors['error_message'] = [{"error": data.get("data"), "data": chunked_data}]
                continue
    
        
        for result in response_json:
            if result.get('new') == True:
                created_count += 1
            elif result.get('new') == False:
                updated_count += 1

        return {
            "created_count": created_count,
            "updated_count": updated_count,
            "error_count": error_count, 
            "details": {"response": response_json,},
            "errors": errors
        }