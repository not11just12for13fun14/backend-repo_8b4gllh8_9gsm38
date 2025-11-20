import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timezone

from database import db, create_document, get_documents

app = FastAPI(title="Ride Social API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RideIn(BaseModel):
    driver_name: str
    car_model: Optional[str] = None
    seats_available: int
    origin: str
    destination: str
    departure_time: str
    contact: str
    notes: Optional[str] = None

class RideOut(RideIn):
    id: str
    created_at: Optional[str] = None

class RideRequestIn(BaseModel):
    requester_name: str
    contact: str
    message: Optional[str] = None

class RideRequestOut(RideRequestIn):
    id: str
    ride_id: str
    status: str
    requested_at: Optional[str] = None


@app.get("/")
def read_root():
    return {"message": "Ride Social API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


@app.get("/api/rides", response_model=List[RideOut])
def list_rides():
    docs = get_documents("ride", {}, limit=100)
    rides: List[RideOut] = []
    for d in docs:
        rides.append(RideOut(
            id=str(d.get("_id")),
            driver_name=d.get("driver_name"),
            car_model=d.get("car_model"),
            seats_available=d.get("seats_available"),
            origin=d.get("origin"),
            destination=d.get("destination"),
            departure_time=d.get("departure_time"),
            contact=d.get("contact"),
            notes=d.get("notes"),
            created_at=d.get("created_at").isoformat() if d.get("created_at") else None,
        ))
    return rides


@app.post("/api/rides", response_model=dict)
def create_ride(ride: RideIn):
    ride_dict = ride.model_dump()
    inserted_id = create_document("ride", ride_dict)
    return {"id": inserted_id}


@app.post("/api/rides/{ride_id}/requests", response_model=dict)
def create_request(ride_id: str, req: RideRequestIn):
    # Validate ride exists
    try:
        oid = ObjectId(ride_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ride id")

    ride = db["ride"].find_one({"_id": oid})
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")

    payload = req.model_dump()
    payload.update({
        "ride_id": ride_id,
        "status": "pending",
        "requested_at": datetime.now(timezone.utc)
    })

    inserted_id = create_document("riderequest", payload)
    return {"id": inserted_id}


@app.get("/api/rides/{ride_id}/requests", response_model=List[RideRequestOut])
def list_requests(ride_id: str):
    docs = get_documents("riderequest", {"ride_id": ride_id}, limit=200)
    results: List[RideRequestOut] = []
    for d in docs:
        results.append(RideRequestOut(
            id=str(d.get("_id")),
            ride_id=d.get("ride_id"),
            requester_name=d.get("requester_name"),
            contact=d.get("contact"),
            message=d.get("message"),
            status=d.get("status"),
            requested_at=d.get("requested_at").isoformat() if d.get("requested_at") else None,
        ))
    return results


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
