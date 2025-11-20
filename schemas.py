"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Example schemas (keep for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# --------------------------------------------------
# Ride sharing app schemas (used by the application)
# --------------------------------------------------

class UserProfile(BaseModel):
    """Basic user profile for drivers/requesters"""
    name: str = Field(..., description="Display name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone")

class Ride(BaseModel):
    """Rides collection schema
    Collection name: "ride"
    """
    driver_name: str = Field(..., description="Driver's name")
    car_model: Optional[str] = Field(None, description="Car make/model")
    seats_available: int = Field(..., ge=1, description="Number of free seats")
    origin: str = Field(..., description="Start location")
    destination: str = Field(..., description="End location")
    departure_time: str = Field(..., description="ISO date-time string for departure")
    contact: str = Field(..., description="How to contact the driver")
    notes: Optional[str] = Field(None, description="Additional details")

class RideRequest(BaseModel):
    """Ride requests collection schema
    Collection name: "riderequest"
    """
    ride_id: str = Field(..., description="Associated ride document id")
    requester_name: str = Field(..., description="Name of the passenger")
    contact: str = Field(..., description="Way to contact the requester")
    message: Optional[str] = Field(None, description="Optional message for the driver")
    status: str = Field("pending", description="pending | accepted | declined")
    requested_at: Optional[datetime] = Field(None, description="Timestamp of request (auto)")

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
