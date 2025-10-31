from appwrite.client import Client
from appwrite.query import Query
from appwrite.services.tables_db import TablesDB
from appwrite.services.storage import Storage
from appwrite.id import ID
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))  # Your Appwrite Endpoint
client.set_project(os.getenv("APPWRITE_PROJECT_ID"))  # Your project ID
client.set_key(os.getenv("APPWRITE_API_KEY"))  # Your secret API key

# Initialize Appwrite services
tables_db = TablesDB(client)
storage = Storage(client)

# Constants for database and collection IDs
Databases_ID = os.getenv("APPWRITE_DATABASE_ID")
Resumes_Collection_ID = "resumes_collection"

# Helper functions for database operations
def save_resume(user_id:str, resume_text:str, file_name:str):
    """Save or update resume text to the database"""
    from datetime import datetime

    # Check if user already has a resume
    try:
        existing = tables_db.list_rows(
            database_id=Databases_ID,
            table_id=Resumes_Collection_ID,
            queries=[Query.equal("user_id", user_id)]
        )

        if existing['total'] > 0:
            # Update existing resume
            row_id = existing['rows'][0]['$id']
            return tables_db.update_row(
                database_id=Databases_ID,
                table_id=Resumes_Collection_ID,
                row_id=row_id,
                data={
                    "resume_text": resume_text,
                    "file_name": file_name
                }
            )
    except Exception as e:
        print(f"No existing resume found: {e}")

    # Create new resume
    return tables_db.create_row(
        database_id=Databases_ID,
        table_id=Resumes_Collection_ID,
        row_id=ID.unique(),
        data={
            "user_id": user_id,
            "resume_text": resume_text,
            "file_name": file_name
        }
    )

def get_resume(user_id:str):
    """Fetch user's resume from the database"""
    result = tables_db.list_rows(
        database_id=Databases_ID,
        table_id=Resumes_Collection_ID,
        queries=[Query.equal("user_id", user_id)]
    )

    if result['total'] > 0:
        return result['rows'][0]
    return None

def delete_resume(user_id:str):
    """Delete user's resume from the database"""
    try:
        existing = tables_db.list_rows(
            database_id=Databases_ID,
            table_id=Resumes_Collection_ID,
            queries=[Query.equal("user_id", user_id)]
        )

        if existing['total']>0:
            row_id = existing['rows'][0]['$id']
            tables_db.delete_row(
                database_id=Databases_ID,
                table_id=Resumes_Collection_ID,
                row_id=row_id
            )
            return True
    except Exception as e:
        print(f"Error deleting resume: {e}")
    return False