#!/usr/bin/env python3
"""
Test script for the database-integrated Gameserver API.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_create_gameserver():
    print("🧪 Testing Database-Integrated Gameserver API")
    print("=" * 50)
    
    # Simplified gameserver payload (only game_id and config needed)
    gameserver_data = {
        "user_id": "sakalivan4",
        "game_id": 1,  # Assuming you have a game with ID 1 in the database
        "config_data": {
            "EULA": "true",
            # "DIFFICULTY": "normal",
            # "MODE": "survival",
            # "MOTD": "Welcome to my server!"
        }
    }
    
    # Create first gameserver
    print("\n1. ➕ Creating first gameserver...")
    response = requests.post(f"{BASE_URL}/gameservers/", json=gameserver_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        server1 = response.json()
        print(f"✅ Created gameserver: {server1['server_id']}")
        server1_id = server1["server_id"]
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Create second gameserver with different config
    # print("\n2. ➕ Creating second gameserver...")
    # gameserver_data["config_data"]["MOTD"] = "Another server!"
    # gameserver_data["config_data"]["DIFFICULTY"] = "hard"
    """
    response = requests.post(f"{BASE_URL}/gameservers/", json=gameserver_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        server2 = response.json()
        print(f"✅ Created gameserver: {server2['server_id']}")
        server2_id = server2["server_id"]
        
        # Verify IDs are different
        if server1_id != server2_id:
            print(f"✅ Server IDs are unique: {server1_id} ≠ {server2_id}")
        else:
            print(f"❌ Server IDs are the same (this shouldn't happen)")
    else:
        print(f"❌ Error: {response.text}")
        return
    
    # Test with invalid game_id
    print("\n3. ❌ Testing invalid game_id...")
    invalid_data = gameserver_data.copy()
    invalid_data["game_id"] = 999  # Non-existent game
    
    response = requests.post(f"{BASE_URL}/gameservers/", json=invalid_data)
    print(f"Status: {response.status_code} (expected 404)")
    if response.status_code == 404:
        print("✅ Correctly rejected invalid game_id")
    
    # Test with invalid config variable
    print("\n4. ❌ Testing invalid config variable...")
    invalid_config_data = gameserver_data.copy()
    invalid_config_data["config_data"]["INVALID_VAR"] = "value"
    
    response = requests.post(f"{BASE_URL}/gameservers/", json=invalid_config_data)
    print(f"Status: {response.status_code} (expected 400)")
    if response.status_code == 400:
        print("✅ Correctly rejected invalid config variable")
        print(f"Error message: {response.json()['detail']}")
    
    # List all gameservers
    print("\n5. 📋 Listing all gameservers...")
    response = requests.get(f"{BASE_URL}/gameservers/")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['total_count']} gameservers:")
        for gs in data['gameservers']:
            print(f"  - {gs['server_id']} (user: {gs['user_id']})")
    
    # Get specific gameserver
    print(f"\n6. 🔍 Getting gameserver {server1_id}...")
    response = requests.get(f"{BASE_URL}/gameservers/{server1_id}")
    if response.status_code == 200:
        print("✅ Successfully retrieved gameserver details")
    else:
        print(f"❌ Error: {response.text}")
    
    # Clean up - delete both servers
    print(f"\n7. 🗑️ Cleaning up...")
    for server_id in [server1_id, server2_id]:
        response = requests.delete(f"{BASE_URL}/gameservers/{server_id}")
        if response.status_code == 200:
            print(f"✅ Deleted {server_id}")
        else:
            print(f"❌ Failed to delete {server_id}: {response.text}")
    """
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    try:
        test_create_gameserver()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure it's running on http://localhost:5000")
        print("Start it with: fastapi dev --port 5000 main.py")
    except Exception as e:
        print(f"❌ Test failed: {e}") 