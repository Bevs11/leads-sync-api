from sqlalchemy.orm import Session
from app.models import ImportLog
from typing import List, Optional, Any
import re

def log_import(
    db: Session,
    total_rows: int,
    created_count: int,
    updated_count: int,
    error_count: int,
    details: Any,
    errors: Any
):
    log = ImportLog(
        total_rows=total_rows,
        created_count=created_count,
        updated_count=updated_count,
        error_count=error_count,
        details=details or {},
        errors=errors or {},
    )
    try:
        db.add(log)
        db.commit()
        db.refresh(log)
    except:
        db.rollback()
        raise
    return log

def check_for_duplicates(leads:List):
    """
    Check for duplicate leads based on email.
    Returns a list of emails that are duplicates.
    """
    seen = set()
    duplicates = set()
    valid_leads = []
    duplicate_leads = []
    
    for lead in leads:
        email = lead.email
        if email in seen:
            duplicates.add(email)
            duplicate_leads.append(lead)
        else:
            seen.add(email)
            valid_leads.append(lead)

    
    return valid_leads, duplicate_leads

def check_for_empty_fields(leads: List):
    """
    Check for empty fields in leads.
    Returns a list of leads with empty fields.
    """
    empty_email = []
    valid_leads = []
    
    for lead in leads:
        if not lead.email:
            empty_email.append(lead)
        else:
            valid_leads.append(lead)
    
    return valid_leads, empty_email
def check_for_email_validity(leads: List):
    """
    Check for valid email format in leads.
    Returns a list of leads with invalid emails.
    """

    invalid_email = []
    valid_leads = []
    
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    
    for lead in leads:
        if not re.match(email_regex, lead.email):
            invalid_email.append(lead)
        else:
            valid_leads.append(lead)
    
    return valid_leads, invalid_email