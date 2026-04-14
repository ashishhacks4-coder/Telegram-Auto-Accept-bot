from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetChatInviteImportersRequest, HideChatJoinRequestRequest
import asyncio
import json
import os

# ✅ DIRECT VALUES (yahi fix hai)
api_id = 39424967
api_hash = "05bd3d0c3625a42301025a48e82e7d19"

client = TelegramClient("session", api_id, api_hash)

CONFIG_FILE = "groups.json"

# Load config
def load_data():
    if not os.path.exists(CONFIG_FILE):
        return {"groups": [], "running": False}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# Save config
def save_data(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# Accept requests loop
async def accept_requests():
    while True:
        data = load_data()

        if not data["running"]:
            await asyncio.sleep(10)
            continue

        for group in data["groups"]:
            try:
                result = await client(GetChatInviteImportersRequest(
                    peer=group,
                    requested=True,
                    limit=10
                ))

                for user in result.importers:
                    await client(HideChatJoinRequestRequest(
                        peer=group,
                        user_id=user.user_id,
                        approve=True
                    ))
                    print(f"✔ Accepted {user.user_id} in {group}")

            except Exception as e:
                print(f"Error in {group}: {e}")

        print("⏳ Waiting 30 min...")
        await asyncio.sleep(1800)

# ================= COMMANDS =================

@client.on(events.NewMessage(pattern=r"\.startbot"))
async def start_bot(event):
    data = load_data()
    data["running"] = True
    save_data(data)
    await event.reply("✅ Bot Started")

@client.on(events.NewMessage(pattern=r"\.stopbot"))
async def stop_bot(event):
    data = load_data()
    data["running"] = False
    save_data(data)
    await event.reply("⛔ Bot Stopped")

@client.on(events.NewMessage(pattern=r"\.add (.+)"))
async def add_group(event):
    group = event.pattern_match.group(1)
    data = load_data()

    if group not in data["groups"]:
        data["groups"].append(group)
        save_data(data)
        await event.reply(f"✅ Added: {group}")
    else:
        await event.reply("⚠️ Already added")

@client.on(events.NewMessage(pattern=r"\.remove (.+)"))
async def remove_group(event):
    group = event.pattern_match.group(1)
    data = load_data()

    if group in data["groups"]:
        data["groups"].remove(group)
        save_data(data)
        await event.reply(f"❌ Removed: {group}")
    else:
        await event.reply("⚠️ Not found")

@client.on(events.NewMessage(pattern=r"\.list"))
async def list_groups(event):
    data = load_data()

    if not data["groups"]:
        await event.reply("❌ No groups added")
    else:
        await event.reply("📋 Groups:\n" + "\n".join(data["groups"]))

# ================= MAIN =================

async def main():
    await client.start()
    print("🚀 Bot Running")
    client.loop.create_task(accept_requests())
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
