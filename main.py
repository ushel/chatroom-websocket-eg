# main.py
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime

from pubsub.pubsub import pubsub
from websocket_manager import manager

app = FastAPI()

# Ensure storage folder exists
os.makedirs("storage", exist_ok=True)


# ---------------------------------------------------------
# SAVE PRIVATE CHAT MESSAGE
# ---------------------------------------------------------
async def save_private_message(topic: str, message: str):
    """
    topic = private:alice-bob -> file = storage/alice_bob.txt
    """
    pair = topic.replace("private:", "")
    file_path = f"storage/{pair}.txt"

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {message}\n")


# ---------------------------------------------------------
# CALLBACK REGISTRY TO PREVENT DUPLICATES
# ---------------------------------------------------------
callback_registry = {}

def get_callback(topic):
    """
    Returns a callback function unique to this topic.
    Prevents duplicate subscriptions that cause multiple writes.
    """
    if topic not in callback_registry:

        async def callback(message, t=topic):
            await save_private_message(t, message)

        callback_registry[topic] = callback

    return callback_registry[topic]


# ---------------------------------------------------------
# MAIN PRIVATE CHAT WEBSOCKET ENDPOINT
# ---------------------------------------------------------
@app.websocket("/ws/private/{user1}/{user2}")
async def private_chat(user1: str, user2: str, websocket: WebSocket):

    # Create normalized topic name (same for both user orders)
    pair = "-".join(sorted([user1, user2]))
    topic = f"private:{pair}"

    # Subscribe the callback ONLY ONCE
    pubsub.subscribe(topic, get_callback(topic))

    # Accept connection
    await manager.connect(user1, user2, websocket)
    print(f"Connected: {user1} ↔ {user2}")

    try:
        while True:
            # Receive user message
            text = await websocket.receive_text()
            message = f"{user1}: {text}"

            # Save message using pub/sub
            await pubsub.publish(topic, message)

            # Send message only to the two users
            await manager.broadcast_private(user1, user2, message)

    except WebSocketDisconnect:
        # Remove connection from manager
        manager.disconnect(user1, user2, websocket)

        # DO NOT CALL websocket.close() → Causes ASGI crash
        print(f"User disconnected: {user1} ↔ {user2}")

