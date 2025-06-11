from decimal import Decimal
from .core.config import config
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel, Relationship
import sqlalchemy as sa
from pydantic import BaseModel as PydanticBaseModel
from typing import Dict, Optional, List


# base model for all models
# makes sure that all models are created in the appropriate schema
class BaseModel(SQLModel):
    pass


# request models
class CreateGameServerRequest(PydanticBaseModel):
    user_id: str
    game_id: int
    config_data: Dict[str, str]

class GameServerResponse(PydanticBaseModel):
    server_id: str
    status: str

# db models
class Game(SQLModel, table=True):
    __tablename__ = "games"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    short_name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    
    docker_image: str = Field(nullable=False)
    cpu_requests: str = Field(nullable=False)
    cpu_limits: str = Field(nullable=False)
    memory_requests: str = Field(nullable=False)
    memory_limits: str = Field(nullable=False)
    
    # Relationships
    versions: List["Version"] = Relationship(back_populates="game", sa_relationship_kwargs={'lazy': 'selectin'})
    config_vars: List["ConfigVar"] = Relationship(back_populates="game", sa_relationship_kwargs={'lazy': 'selectin'})
    port: Optional["Port"] = Relationship(back_populates="game", sa_relationship_kwargs={'lazy': 'selectin'})  # 1-to-1 relationship


class Version(SQLModel, table=True):
    __tablename__ = "versions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tag: str = Field(nullable=False)
    
    # Foreign key
    game_id: int = Field(foreign_key="games.id", nullable=False)
    
    # Relationship
    game: Optional[Game] = Relationship(back_populates="versions", sa_relationship_kwargs={'lazy': 'selectin'})


class ConfigVar(SQLModel, table=True):
    __tablename__ = "config_vars"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    
    # Foreign key
    game_id: int = Field(foreign_key="games.id", nullable=False)
    
    # Relationship
    game: Optional[Game] = Relationship(back_populates="config_vars", sa_relationship_kwargs={'lazy': 'selectin'})


class Port(SQLModel, table=True):
    __tablename__ = "ports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    number: int = Field(nullable=False)
    
    # Foreign key with unique constraint for 1-to-1 relationship
    game_id: int = Field(foreign_key="games.id", nullable=False, unique=True)
    
    # Relationship
    game: Optional[Game] = Relationship(back_populates="port", sa_relationship_kwargs={'lazy': 'selectin'})

