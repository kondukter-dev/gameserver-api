from .. import crud
from ..models import *
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from .deps import get_session
from ..k8.client import k8_cl
from typing import Optional, Dict, Any
import uuid

gameservers_router = APIRouter()

# ========== CRUD ENDPOINTS ==========

@gameservers_router.get("/")
async def list_gameservers():
    """List all gameservers."""
    try:
        gameservers = k8_cl.list_gameservers()
        return {
            "gameservers": gameservers,
            "total_count": len(gameservers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list gameservers: {str(e)}")

@gameservers_router.get("/{server_id}")
async def get_gameserver(server_id: str):
    """Get a single gameserver by server_id."""
    try:
        gameserver = k8_cl.get_gameserver(server_id)
        if gameserver is None:
            raise HTTPException(status_code=404, detail=f"Gameserver {server_id} not found")
        return gameserver
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gameserver: {str(e)}")

@gameservers_router.post("/", response_model=GameServerResponse)
async def create_gameserver(request: CreateGameServerRequest, session: AsyncSession = Depends(get_session)):
    """Create a new gameserver using game configuration from database."""
    try:
        # Generate a unique server ID
        server_id = uuid.uuid4().hex
        
        # Fetch game data from database with all relationships
        statement = select(Game).where(Game.id == request.game_id)
        result = await session.execute(statement)
        game = result.scalar_one_or_none()
        
        if not game:
            raise HTTPException(status_code=404, detail=f"Game with id {request.game_id} not found")
        
        # Validate that the game has a port configured
        if not game.port:
            raise HTTPException(status_code=400, detail=f"Game {game.name} does not have a port configured")
        
        # Validate config variables against game's allowed config vars
        game_config_var_names = {var.name for var in game.config_vars}
        provided_config_keys = set(request.config_data.keys())
        
        # Check for invalid config keys
        invalid_keys = provided_config_keys - game_config_var_names
        if invalid_keys:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid config variables for game {game.name}: {list(invalid_keys)}. "
                       f"Allowed variables: {list(game_config_var_names)}"
            )
        
        # Create gameserver using database configuration
        result = k8_cl.create_gameserver(
            server_id=server_id,
            game_name=game.short_name,
            user_id=request.user_id,
            image=game.docker_image,
            requests_memory=game.memory_requests,
            requests_cpu=game.cpu_requests,
            limits_memory=game.memory_limits,
            limits_cpu=game.cpu_limits,
            game_port=game.port.number,
            config_data=request.config_data
        )
        
        return GameServerResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create gameserver: {str(e)}")

@gameservers_router.delete("/{server_id}", response_model=GameServerResponse)
async def delete_gameserver(server_id: str):
    """Delete a gameserver."""
    try:
        result = k8_cl.delete_gameserver(server_id)
        
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Gameserver {server_id} not found")
        
        return GameServerResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete gameserver: {str(e)}")

# ========== ADDITIONAL ENDPOINTS ==========

@gameservers_router.get("/pods/all")
async def get_all_pods():
    """Get all pods in the gameserver namespace (original endpoint)."""
    pods = k8_cl.v1_api.list_namespaced_pod(
        namespace=k8_cl.namespace
    )
    return pods.to_dict()

@gameservers_router.get("/{server_id}/status")
async def get_gameserver_status(server_id: str):
    """Get simplified status of a gameserver."""
    try:
        gameserver = k8_cl.get_gameserver(server_id)
        if gameserver is None:
            raise HTTPException(status_code=404, detail=f"Gameserver {server_id} not found")
        
        # Extract simplified status information
        deployment = gameserver["deployment"]
        pods = gameserver["pods"]
        
        pod_statuses = []
        if pods["items"]:
            for pod in pods["items"]:
                pod_statuses.append({
                    "name": pod["metadata"]["name"],
                    "phase": pod["status"]["phase"],
                    "ready": pod["status"].get("conditions", [])
                })
        
        return {
            "server_id": server_id,
            "deployment_status": {
                "ready_replicas": deployment["status"].get("ready_replicas", 0),
                "replicas": deployment["spec"]["replicas"],
                "available_replicas": deployment["status"].get("available_replicas", 0)
            },
            "pods": pod_statuses
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gameserver status: {str(e)}")