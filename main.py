#fastapi code here
from fastapi import FastAPI, Request, Response, status, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from fastapi import Body
from DB_operations import add_user, get_all_users, search_user_by_aadhaar, get_user_by_id, update_user, delete_user, get_facilities_by_district
from LLM_inference import invoke_nvidia_llm
from message import send_sms_message
import firebase_admin
from firebase_admin import credentials, firestore

app = FastAPI(root_path="/api")
# app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/users/")
async def create_migrant(migrant: dict = Body(...)):
    result = add_user(migrant)
    if result.get("success"):
        return {"message": "Migrant created", "id": str(result["id"].id)}
    return JSONResponse(status_code=400, content={"error": result.get("error")})

@app.get("/users/")
async def list_migrants():
    result = get_all_users()
    if result.get("success"):
        return result["data"]
    return JSONResponse(status_code=400, content={"error": result.get("error")})

@app.get("/users/by-aadhaar/{aadhaar_number}")
async def get_migrant_by_aadhaar(aadhaar_number: str):
    result = search_user_by_aadhaar(aadhaar_number)
    if result.get("success"):
        return result["data"]
    return JSONResponse(status_code=404, content={"error": result.get("error")})

@app.get("/users/id/{user_id}")
async def get_migrant_by_id(user_id: str):
    result = get_user_by_id(user_id)
    if result.get("success"):
        return result["data"]
    return JSONResponse(status_code=404, content={"error": result.get("error")})

@app.put("/users/id/{user_id}")
async def update_migrant(user_id: str, update_data: dict = Body(...)):
    result = update_user(user_id, update_data)
    if result.get("success"):
        return {"message": "Migrant updated"}
    return JSONResponse(status_code=404, content={"error": result.get("error")})

@app.delete("/users/id/{user_id}")
async def delete_migrant(user_id: str):
    result = delete_user(user_id)
    if result.get("success"):
        return {"message": "Migrant deleted"}
    return JSONResponse(status_code=404, content={"error": result.get("error")})

@app.get("/users/{aadhaar_id}")
async def get_migrant_records(aadhaar_id: str):
    # Query DB for migrant health records by aadhaar_id
    # If found, return records, else 404
    return {"aadhaar": aadhaar_id, "records": "Sample records here"}

@app.get("/facilities/")
async def facilities_by_district(district: str = Query(..., description="Kerala district name")):
    result = get_facilities_by_district(district)

    if not result.get("success"):
        return JSONResponse(status_code=404, content={"error": result.get("error")})

    district_name = result["district"]
    facilities = result["facilities"]

    response = {}
    for idx, facility in enumerate(facilities, start=1):
        response[f"facility_{idx}"] = {
            "district": district_name,
            "facilityName": facility.get("facilityName"),
            "phoneNumbers": facility.get("phoneNumbers", []),
            "address": facility.get("address"),
            "facilityType": facility.get("facilityType"),
            "services": facility.get("services", []),
            "workingHours": facility.get("workingHours"),
            "remarks": facility.get("remarks", "")
        }

    return response


@app.post("/send-reminder/")
async def send_reminder(aadhaar_id: str):
    # Fetch user data from DB by Aadhaar
    user_result = search_user_by_aadhaar(aadhaar_id)
    if not user_result.get("success") or not user_result.get("data"):
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_result["data"][0]  # Assuming single match

    prompt = f"""
    User Details:
    Name: {user_data['name']}
    Age: {user_data.get('age', 'N/A')}
    Blood Group: {user_data.get('blood_group', 'N/A')}
    Language: {user_data.get('language', 'en')}
    Address: {user_data['address']}
    Vaccination Status: {user_data['records']}
    Special Notes: {user_data['records'].get('specialNotes', 'None')}
    Companies Worked: {[c['name'] for c in user_data['companies']]}
    
    Based on these details, generate a brief health advisory message for reminders.
    """

    # Call Nvidia LLM inference
    llm_response = invoke_nvidia_llm(prompt)
    if "error" in llm_response:
        raise HTTPException(status_code=500, detail=llm_response["error"])

    advisory_message = llm_response.get("advice", ["Please follow up with nearest health facility"])[0]

    # Send SMS in user's preferred language (assuming English here, can add translation logic)
    phone_number = str(user_data.get("phonenumber"))
    if not phone_number:
        raise HTTPException(status_code=400, detail="User phone number missing")

    sms_sid = send_sms_message(phone=phone_number, message=advisory_message)

    return {"message": "Reminder sent successfully", "sms_sid": sms_sid}
