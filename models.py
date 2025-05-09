from decimal import Decimal
from .core.config import config
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel
import sqlalchemy as sa


# base model for all models
# makes sure that all models are created in the appropriate schema
class BaseModel(SQLModel):
    pass


# request models

# db models

