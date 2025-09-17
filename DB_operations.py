# CRUD operaions here

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("ps82-stellarythm-firebase-adminsdk-fbsvc-de4ed2b41c.json")
app = firebase_admin.initialize_app(cred)
# print(app)
db = firestore.client()
# print(db)


def add_user(data):
    """
    Adds a new user document to the 'users' collection in the database.

    Schema for `data` argument:
        {
            "name": str,
            "age": int,
            "blood_group": str,
            "address": str,
            "aadhaarNumber": str,
            "phonenumber": int,
            "originState": str,
            "originDistrict": str,
            "destinationDistrict": str,
            "records": {
                "vaccination1": bool,
                "vaccination2": bool,
                "specialNotes": str
            },
            "companies": [
                {
                    "name": str,
                    "from": str (YYYY-MM-DD),
                    "to": Optional[str] (YYYY-MM-DD or None),
                    "working": bool
                },
                ...
            ]
        }

    Args:
        data (dict): A dictionary containing user information to be added to the database.

    Returns:
        dict: A dictionary indicating the success status of the operation.
            If successful, returns {"success": True, "id": <update_time>}, where <update_time> is the update time of the document.
            If failed, returns {"success": False, "error": <error_message>}, where <error_message> is the exception message.
    """

    try:
        doc_ref = db.collection('users').add(data)
        return {"success": True, "id": doc_ref[1]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_by_id(user_id):
    """
    Retrieves a user document from the 'users' collection by user ID.

    Args:
        user_id (str): The unique document ID of the user.

    Returns:
        dict: If successful, returns {"success": True, "data": <user_data_dict>}, where <user_data_dict> is the user document.
            If not found, returns {"success": False, "error": "User not found"}.
            If failed, returns {"success": False, "error": <error_message>}.
    """
    
    try:
        doc = db.collection('users').document(user_id).get()
        if doc.exists:
            return {"success": True, "data": doc.to_dict()}
        else:
            return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_user(user_id, update_data):
    """
    Updates an existing user document in the 'users' collection.

    Args:
        user_id (str): The unique document ID of the user to update.
        update_data (dict): A dictionary containing the fields to update.

    Returns:
        dict: If successful, returns {"success": True}.
            If not found, returns {"success": False, "error": "User not found"}.
            If failed, returns {"success": False, "error": <error_message>}.
    """
    try:
        doc_ref = db.collection('users').document(user_id)
        if doc_ref.get().exists:
            doc_ref.update(update_data)
            return {"success": True}
        else:
            return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_user(user_id):
    """
    Deletes a user document from the 'users' collection by user ID.

    Args:
        user_id (str): The unique document ID of the user to delete.

    Returns:
        dict: If successful, returns {"success": True}.
            If not found, returns {"success": False, "error": "User not found"}.
            If failed, returns {"success": False, "error": <error_message>}.
    """
    try:
        doc_ref = db.collection('users').document(user_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return {"success": True}
        else:
            return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_all_users():
    """
    Retrieves all user documents from the 'users' collection.

    Returns:
        dict: If successful, returns {"success": True, "data": <user_list>}, where <user_list> is a list of user documents with their IDs.
            If failed, returns {"success": False, "error": <error_message>}.
    """
    try:
        users = db.collection('users').stream()
        user_list = [{**doc.to_dict(), "id": doc.id} for doc in users]
        return {"success": True, "data": user_list}
    except Exception as e:
        return {"success": False, "error": str(e)}
    



def search_user_by_aadhaar(aadhaar_number):
    """
    Searches for a user document in the 'users' collection by Aadhaar number.

    Args:
        aadhaar_number (str): The Aadhaar number to search for.

    Returns:
        dict: If successful, returns {"success": True, "data": <user_list>}, where <user_list> is a list of matching user documents with their IDs.
            If failed, returns {"success": False, "error": <error_message>}.
    """
    try:
        query = db.collection('users').where('aadhaarNumber', '==', aadhaar_number).stream()
        results = [{**doc.to_dict(), "id": doc.id} for doc in query]
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}





#below code will be used for testing and will only run from this file
def main():
    # Example data
    user_dataa = {
        "name": "Jane Doe",
        "age": 57,
        "blood_group": "A+",
        "language": "en",
        "address": "456 Avenue Name",
        "aadhaarNumber": "9876-5432-1898",
        "phonenumber": 7887788778,
        "originState": "Kerala",
        "originDistrict": "Ernakulam",
        "destinationDistrict": "Cuttack",
        "records": {
            "vaccination1": True,
            "vaccination2": True,
            "specialNotes": "None"
        },
        "companies": [
            {
                "name": "DEF Industries",
                "from": "xxxxxxxxxxxxxx",
                "to": "2024-01-31",
                "working": False
            },
            {
                "name": "GHI Services",
                "from": "2024-02-01",
                "to": None,
                "working": True
            }
        ]
    }

    # Add user
    add_result = add_user(user_dataa)
    print("Add User Result:", add_result)

    if add_result.get("success"):
        # Get all users
        all_users = get_all_users()
        print("All Users:", all_users)

        # Get user by ID
        user_id = add_result["id"].id      #add_result["id"].path.split("/")[-1]
        # print(user_id,"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        if user_id:
            get_result = get_user_by_id(user_id)
            print("Get User Result:", get_result)

            # Update user
            update_data = {"address": "789 New Address"}
            update_result = update_user(user_id, update_data)
            print("Update User Result:", update_result)

            # Search user by Aadhaar number
            search_result = search_user_by_aadhaar(user_dataa["aadhaarNumber"])
            print("Search User by Aadhaar Result:", search_result)

            # Delete user
            # delete_result = delete_user(user_id)
            # print("Delete User Result:", delete_result)
        else:
            print("Could not determine user ID for further operations.")
    else:
        print("User addition failed, skipping further operations.")

if __name__ == "__main__":
    main()