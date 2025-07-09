from datetime import date, time
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel, Column, String, Text


# Common base model for the Party resource.
# Defines shared fields used by both the database and from models
class PartyBase(SQLModel):
    party_date: date
    party_time: time
    invitation: str = Field(sa_column=Column(Text), min_length=10)
    venue: str = Field(sa_column=Column(String(100)))


# Database model for the Party resource.
# Inherits from PartyBase and represents the actual table, including relationships.
class Party(PartyBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    # Defines ORM relationship: party.gifts returns associated Gifts objects.
    gifts: List["Gift"] = Relationship(back_populates="party")
    # Defines ORM relationship: party.guests returns associated Guest objects.
    guests: List["Guest"] = Relationship(back_populates="party")


# Form model for the Party resource.
# Used by FastAPI to validate and process incoming form data for Party operations.
class PartyForm(PartyBase):
    pass


# Common base model for the Gift resource.
# Contains shared fields used by both the database and form models.
class GiftBase(SQLModel):
    gift_name: str = Field(sa_column=Column(String(100)))
    price: Decimal = Field(decimal_places=2, ge=0)
    link: Optional[str]
    # Defines a foreign key connecting the gift to a party at the database level.
    party_id: UUID = Field(default=None, foreign_key="party.uuid")


# Database model for the Gift resource.
# Inherits from GiftBase and represents the gift table, incluiding its relationship to Party.
class Gift(GiftBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    # Defines ORM relationship: gift.party returns the associated Party object.
    party: Party = Relationship(back_populates="gifts")


# Form model for the Gift resource.
# Used for validating and processing incoming gift data via FastAPI
class GiftForm(GiftBase):
    pass


# Common base model for the Guest resource.
# Defines shared fields used by both the database and form models.
class GuestBase(SQLModel):
    name: str = Field(sa_column=Column(String(100)))
    attending: bool = False
    # Defines a foreign key connecting the guest to a party at the database level.
    party_id: UUID = Field(default=None, foreign_key="party.uuid")


# Database model for the Guest resource.
# Inherits from GuestBase and maps to the guest table, including its relationship to Party.
class Guest(GuestBase, table=True):
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    # Establishes ORM relationship: guest.party returns the associated Party object.
    party: Party = Relationship(back_populates="guests")


# Form model for the Guest resource.
# Used by FastAPI for validating and processing incoming guest data.
class GuestForm(GuestBase):
    pass
