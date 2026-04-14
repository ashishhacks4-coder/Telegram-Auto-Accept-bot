from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetChatInviteImportersRequest, HideChatJoinRequestRequest
from telethon.sessions import StringSession
import asyncio
import json
import os

# ✅ TERA API
api_id = 39424967
api_hash = "05bd3d0c3625a42301025a48e82e7d19"

# 🔥 SESSION STRING
SESSION = "1AZWarzkBu2r43lBZhVCIPXZ8rglNhTXifw5XYWyO4KPt4rbSkv02KsOABHKIk0NUt7FRyKEK5rTYBm8xcMksVcR4l8toPg7kTTx0DfCG-58fCCn6NhcQEFTkyjpgNtTzhU859dGvokTm8l1ocSBtIIabd-PWTiFLdSLXaT6fsicqtBVRGprLF1fne_vV19oAswKmhqWooPX_onZo_oltbPfKyAdE6MDOcRIJfz8nvN6GPFTIDXUoM7PqIlS_M9Cof9ex6j8iT6ZcDEHqNc-FxJPO6R8zmeUpLxAWZrIWxC9GenoIdhmiOAh_Hab94O0giCsrkoxU1KShV8D2AxhreYrApbcn4pQ="

# 🔐 OWNER ID (yaha apna daal)
OWNER_ID = 7937274131   # <-- CHANGE THIS

client = TelegramClient(StringSession(SESSION), api_id, api_hash)

CONFIG_FILE = "groups.json"

# Load config
def load_data():
    if not os.path.exists(CONFIG_FILE):
        return {
            "groups": [],
            "running": False,
            "interval": 1800,
            "accepted": 0
        }
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

# Save config
def save_data(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# 🔄 Accept requests loop
async def accept_requests():
    while True:
        data = load_data()

        if not data["running"]:
            await asyncio.sleep(10)
            continue

        total_accepted = 0

        for group in data["groups"]:
            try:
                result = await client(GetChatInviteImportersRequest(
                    peer=group,
                    requested=True,
                    limit=10
                ))

                if not result.importers:
                    continue

                for user in result.importers:
                    await client(HideChatJoinRequestRequest(
                        peer=group,
                        user_id=user.user_id,
                        approve=True
                    ))
                    total_accepted += 1
                    print(f"✔ Accepted {user.user_id} in {group}")

            except Exception as e:
                print(f"⚠️ Error in {group}: {e}")

        # stats update
        data["accepted"] += total_accepted
        save_data(data)

        print(f"📊 Accepted this round: {total_accepted}")
        print(f"⏳ Waiting {data['interval']} sec...")

        await asyncio.sleep(data["interval"])

# ================= COMMANDS =================

def is_owner(event):
    return event.sender_id == OWNER_ID

@client.on(events.NewMessage(pattern=r"\.startbot"))
async def start_bot(event):
    if not is_owner(event): return
    data = load_data()
    data["running"] = True
    save_data(data)
    await event.reply("✅ Bot Started")

@client.on(events.NewMessage(pattern=r"\.stopbot"))
async def stop_bot(event):
    if not is_owner(event): return
    data = load_data()
    data["running"] = False
    save_data(data)
    await event.reply("⛔ Bot Stopped")

@client.on(events.NewMessage(pattern=r"\.add (.+)"))
async def add_group(event):
    if not is_owner(event): return
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
    if not is_owner(event): return
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
    if not is_owner(event): return
    data = load_data()

    if not data["groups"]:
        await event.reply("❌ No groups added")
    else:
        await event.reply("📋 Groups:\n" + "\n".join(data["groups"]))

# 📊 STATS
@client.on(events.NewMessage(pattern=r"\.stats"))
async def stats(event):
    if not is_owner(event): return
    data = load_data()
    await event.reply(
        f"📊 Total Accepted: {data['accepted']}\n"
        f"⏱ Interval: {data['interval']} sec\n"
        f"📂 Groups: {len(data['groups'])}"
    )

# ⏱ TIMER
@client.on(events.NewMessage(pattern=r"\.settime (\d+)"))
async def set_time(event):
    if not is_owner(event): return
    new_time = int(event.pattern_match.group(1))
    data = load_data()

    data["interval"] = new_time
    save_data(data)

    await event.reply(f"⏱ Timer set to {new_time} sec")

# ================= MAIN =================

async def main():
    await client.start()
    print("🚀 Bot Running")
    client.loop.create_task(accept_requests())
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
