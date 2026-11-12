import asyncio
import json
import math
import os
import random
import threading
import urllib.parse
from pathlib import Path

try:
    import httpx
    import requests
    import pyperclip
    import websockets
    import dearpygui.dearpygui as dpg
except ImportError:
    modules = ["httpx", "requests", "pyperclip", "websockets", "dearpygui"]
    for index, module in enumerate(modules, start=1):
        print(f"[!] Installing {module} | {index} / {len(modules)}")
        os.system(f"python -m pip install {module} -q")
        print(f"[!] Successfully installed {module}\n")

    import httpx
    import requests
    import pyperclip
    import websockets
    import dearpygui.dearpygui as dpg

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = Path(__file__).resolve().parent / "Assets"
VERSION_URL = "https://raw.githubusercontent.com/YeetDisDude/pg3d-tools/main/version.txt"
VERSION = "0.2.1"


def set_status(tag, message):
    if dpg.does_item_exist(tag):
        dpg.set_value(tag, message)


def check_update():
    set_status("updatetxt", "Status: Checking for updates...")
    try:
        r = httpx.get(VERSION_URL, timeout=15)
        latest = r.text.strip()
    except Exception:
        set_status("updatetxt", "Status: Unable to check for updates.")
        return

    if latest != VERSION:
        set_status(
            "updatetxt",
            f"Status: Version {VERSION} is outdated! Download the latest version from github.com/YeetDisDude/pg3d-tools",
        )
    else:
        set_status("updatetxt", f"Status: Pixel Gun 3D Tools version {VERSION} is up to date!")


class Connection:
    @staticmethod
    def threadFunction(ws):
        pass

    @staticmethod
    async def handleSioQueue(ws):
        r = await ws.recv()
        if r.startswith('0{"sid":'):
            r_trim = r[len("0") :]
            loaded_trim = json.loads(r_trim)
            sid = loaded_trim["sid"]
            print(f"Session ID: {sid}")
            r = await ws.recv()
            if r == "40":
                await ws.send("40/sio")
                r = await ws.recv()
                if r == "40/sio":
                    return True, "HANDLE_SQ"
                return False, "IP_BAN"
            return False, "INVALID_RESPONSE"
        return False, "INVALID_SID"

    @staticmethod
    async def sendMessage(ws, message):
        await ws.send('452-/sio,[{"_placeholder":true, "num":0}, {"_placeholder":true, "num":1}]')
        await ws.send(message)
        return True, "SENT"

    @staticmethod
    async def startConnection(message):
        async with websockets.connect(
            "wss://server-v2.pixelgunserver.com:443/socket.io/?EIO=4&transport=websocket&client_ver=v2"
        ) as ws:
            thread = threading.Thread(target=Connection.threadFunction, args=(ws,))
            thread.daemon = True
            thread.start()

            res, mess = await Connection.handleSioQueue(ws)
            if res and mess == "HANDLE_SQ":
                res, mess = await Connection.sendMessage(ws, message)
                if res and mess == "SENT":
                    return True, "Success: Sent"
            elif not res and mess == "IP_BAN":
                return False, "Status: IP Banned | Failed"
            elif not res and mess == "INVALID_RESPONSE":
                return False, "Status: Invalid Server Response | Failed"
            elif not res and mess == "INVALID_SID":
                return False, "Status: Invalid SID Response | Failed"
            return False, "Status: WebSocket request failed"


def encodejsonurl(payload):
    return urllib.parse.quote(json.dumps([payload]))


def checkban(sender, data):
    usrid = dpg.get_value("usrid")
    set_status("status_text", "Status: Sending Request to Pixel Gun 3D Servers...")
    try:
        response = httpx.post(
            "https://secure.pixelgunserver.com/pixelgun3d-config/getBanList.php",
            data={"type_device": int(random.random() * 69), "id": str(usrid)},
            timeout=20,
        ).text
    except Exception:
        set_status("status_text", "Status: Request failed while checking ban status.")
        return

    if response == "1":
        set_status("status_text", f"Status: User ID {usrid} is banned!")
    else:
        set_status("status_text", f"Status: User ID {usrid} is not banned.")


def downloaddumpcs(sender, data):
    version = dpg.get_value("dumpcsvercombo")
    if version == "Select Version":
        set_status("statustxt2", "Status: Please select a version")
        return

    try:
        r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/dumpcs.json", timeout=20)
        r.raise_for_status()
        data = r.json()
        url = data["versions"][version]
    except Exception:
        set_status("statustxt2", "Status: Failed to load version list.")
        return

    download_dir = PROJECT_ROOT / "downloads"
    download_dir.mkdir(exist_ok=True)
    filepath = download_dir / f"{version}.cs"

    set_status("statustxt2", f"Status: Downloading {version}'s Dump.cs...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        file_size = int(response.headers.get("Content-Length", 0) or 0)
        downloaded = 0
        with open(filepath, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    handle.write(chunk)
                    handle.flush()
                    downloaded += len(chunk)
                    if file_size:
                        progress = math.ceil(downloaded / file_size * 100)
                        dpg.set_value("statustxt2", f"Status: Downloading {version}'s Dump.cs... ({progress}%)")
        set_status("statustxt2", f"Status: Downloaded {version} to {filepath}")
    except Exception:
        set_status("statustxt2", f"Status: Failed to download {version}'s Dump.cs.")


def downloadassembly(sender, data):
    version = dpg.get_value("assemblyvercombo")
    if version == "Select Version":
        set_status("statustxt3", "Status: Please select a version")
        return

    try:
        r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/dumpcs.json", timeout=20)
        r.raise_for_status()
        data = r.json()
        url = data["versions"][version]
    except Exception:
        set_status("statustxt3", "Status: Failed to load version list.")
        return

    download_dir = PROJECT_ROOT / "downloads"
    download_dir.mkdir(exist_ok=True)
    filepath = download_dir / f"{version}.dll"

    set_status("statustxt3", f"Status: Downloading {version}'s Assembly-CSharp.dll...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        file_size = int(response.headers.get("Content-Length", 0) or 0)
        downloaded = 0
        with open(filepath, "wb") as handle:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    handle.write(chunk)
                    handle.flush()
                    downloaded += len(chunk)
                    if file_size:
                        progress = math.ceil(downloaded / file_size * 100)
                        dpg.set_value("statustxt3", f"Status: Downloading {version}'s Assembly-CSharp.dll... ({progress}%)")
        set_status("statustxt3", f"Status: Downloaded {version} to {filepath}")
    except Exception:
        set_status("statustxt3", f"Status: Failed to download {version}'s Assembly-CSharp.dll.")


def currencythreshold(sender, data):
    dpg.set_value("coins", "Coins: sending request...")
    dpg.set_value("gems", "Gems: sending request...")
    platform = dpg.get_value("os") if dpg.does_item_exist("os") else "Android"
    platform = "ios" if str(platform).lower() == "ios" else "android"
    try:
        r = httpx.get(f"https://secure.pixelgunserver.com/pixelgun3d-config/advert-v2/advert-{platform}.json", timeout=20)
        r.raise_for_status()
        j = r.json()
        dpg.set_value("coins", f"Coins: {j['cheater']['gemThreshold']}")
        dpg.set_value("gems", f"Gems: {j['cheater']['coinThreshold']}")
    except Exception:
        dpg.set_value("coins", "Coins: request failed")
        dpg.set_value("gems", "Gems: request failed")


def updateplayerlogs(sender, data):
    usrid = dpg.get_value("userid")
    currency = dpg.get_value("currency")
    amount = dpg.get_value("amount")
    times = dpg.get_value("times")

    try:
        times = int(times)
    except ValueError:
        set_status("statustxt", "Status: Times must be a number.")
        return

    parameters = encodejsonurl(
        {
            "cmid": 3783,
            "eid": 1012,
            "uid": str(usrid),
            "dev": 1,
            "c": "NIG",
            "p": 1,
            "v": "69.0.0",
            "r": 1,
            "cid": "1",
            "t": 1,
            "reg": 1,
            "pl": 0,
            "ip1": amount,
            "sp1": currency,
            "sp2": "YeetDisDude",
        }
    )

    count = 0
    try:
        for _ in range(times):
            count += 1
            r = requests.post(
                "https://pixelgun-cl-stat.pixelgunserver.com/event_stat_add_pl.php",
                params=f"muid={str(usrid)}&events={parameters}",
                timeout=20,
            )
            dpg.set_value("statustxt", f"Status: {count} / {times} | Status: {r.status_code} | Response: {r.text.strip()}")
    except requests.exceptions.RequestException:
        set_status("statustxt", "Status: Something went wrong when sending the request...")
        return

    set_status("statustxt", "Status: Finished sending!")


def spamcontacts():
    name = dpg.get_value("name")
    message = dpg.get_value("message")
    numthreads = dpg.get_value("threads")
    email = dpg.get_value("email")

    def send_request(payload):
        with httpx.Client() as client:
            r = client.post("https://lightmap.com/contact_form", data=payload, timeout=20)
            dpg.set_value("statustxt6", f"Status: {r.status_code} | Response: {r.text}")

    try:
        numthreads = max(1, int(numthreads))
    except ValueError:
        set_status("statustxt6", "Status: Threads must be a number.")
        return

    payload = {"name": name, "email": email, "message": message}
    threads = []
    for _ in range(numthreads):
        t = threading.Thread(target=send_request, args=(payload,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    set_status("statustxt6", "Status: Done.")


def makeusername():
    username = dpg.get_value("username")
    newusername = f"⁬{username}"
    dpg.set_value("usernameoutput", newusername)
    set_status("statustxt7", "Status: Complete, copied to clipboard (invisible character added)")
    if pyperclip is not None:
        try:
            pyperclip.copy(newusername)
        except Exception:
            pass


def skinplist():
    skinbase64 = dpg.get_value("skinb64")
    skinname = dpg.get_value("skinname")
    directory = PROJECT_ROOT / "generated"
    directory.mkdir(exist_ok=True)
    filepath = directory / "dict.txt"
    with open(filepath, "w", encoding="utf-8") as handle:
        content = f"""
User Skins:
    <key>User Skins</key>
    <string>{{'1001': {skinbase64}}}</string>
Plist for Skin Names:
    <key>User Name Skins</key>
    <string>{{'1001': {skinname}}}</string>
Current Equipped Skin:
    <key>Name Current Skin</key>
    <string>1001</string>

Usage: Replace the lines in the plist with the lines generated by PG3D Tools
https://github.com/YeetDisDude/
Made by: YeetDisDude
"""
        content = content.replace("'", '"')
        handle.write(content)
    set_status("statustxt8", f"Status: Saved to {filepath}")


def wsMain():
    msg = str(dpg.get_value("msg"))
    try:
        asyncio.run(Connection.startConnection(msg))
    except Exception as exc:
        dpg.set_value("ws_status", f"Status: {exc}")
    else:
        dpg.set_value("ws_status", "Status: Sent")


def searchwep(sender, data):
    searchterm = dpg.get_value("wepsearchterm")
    try:
        r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/weapons.json", timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        dpg.set_value("weaponidresult", "Failed to load weapon list.")
        return

    lower_term = str(searchterm).lower()
    weapon_results = []
    for weapon in data:
        weapon_name = str(weapon.get("weaponname", ""))
        gallery_number = str(weapon.get("gallery_number", ""))
        if lower_term in weapon_name.lower() or searchterm == gallery_number:
            weapon_result = f"""
Weapon Name: {weapon.get('weaponname', '')}
Weapon ID: {weapon.get('weapon_id', '')}
Gallery Number: {weapon.get('gallery_number', '')}"""
            weapon_results.append(weapon_result)
    if not weapon_results:
        weapon_results.append(f"'{searchterm}' not found")
    dpg.set_value("weaponidresult", "\n".join(weapon_results))


def searchwear(sender, data):
    searchterm = dpg.get_value("wearsearchterm")
    try:
        r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/wears.json", timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        dpg.set_value("wearidresult", "Failed to load wear list.")
        return

    lower_term = str(searchterm).lower()
    wear_results = []
    for wear in data:
        wear_name = str(wear.get("wearname", ""))
        wear_id = str(wear.get("wearid", ""))
        if lower_term in wear_name.lower() or searchterm == wear_id:
            wear_result = f"""
Wear Name: {wear.get('wearname', '')}
Wear ID: {wear.get('wearid', '')}"""
            wear_results.append(wear_result)
    if not wear_results:
        wear_results.append(f"'{searchterm}' not found")
    dpg.set_value("wearidresult", "\n".join(wear_results))


def searchitemrecord(sender, data):
    searchterm = dpg.get_value("itemrecordsearchterm")
    try:
        r = requests.get("https://raw.githubusercontent.com/TonicBoomerKewl/pixel-gun-3d-console-client/main/PG3D-ItemRecords.json", timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        dpg.set_value("itemrecordresult", "Failed to load item records.")
        return

    lower_term = str(searchterm).lower()
    item_results = []
    for record_key, record_value in data.items():
        if lower_term in str(record_value).lower() or str(searchterm) == str(record_key):
            item_result = f"""
Item ID: {record_key}
Item Name: {record_value}"""
            item_results.append(item_result)
    if not item_results:
        item_results.append(f"'{searchterm}' not found")
    dpg.set_value("itemrecordresult", "\n".join(item_results))


def searchwscmd(sender, data):
    searchterm = dpg.get_value("wscmdsearchterm")
    try:
        r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/websocketcommand.json", timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        dpg.set_value("wscmdresult", "Failed to load websocket command list.")
        return

    lower_term = str(searchterm).lower()
    cmdresults = []
    for record_value in data:
        if lower_term in str(record_value).lower():
            cmdresults.append(f"\nCommand: {record_value}")
    if not cmdresults:
        cmdresults.append(f"'{searchterm}' not found")
    dpg.set_value("wscmdresult", "\n".join(cmdresults))


def getallscenes():
    try:
        r = httpx.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/scenes.json", timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        dpg.set_value("allscenes", "Failed to load scene list.")
        return

    scenes = []
    for scene in data:
        for _, value in scene.items():
            scenes.append(value)
    dpg.set_value("allscenes", "\n".join(scenes))


def colorpicker(sender, data):
    color = dpg.get_value(sender)
    print(color)


def tab1():
    with dpg.group():
        with dpg.collapsing_header(label="Download Dump.cs files"):
            try:
                r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/dumpcs.json", timeout=20)
                data = r.json()
                vers = list(data["versions"].keys())
            except Exception:
                vers = []
            dpg.add_combo(items=vers, default_value="Select Version", label="Version", tag="dumpcsvercombo", width=150)
            dpg.add_button(label="Download", callback=downloaddumpcs)
            dpg.add_text("Status: ", tag="statustxt2")

        with dpg.collapsing_header(label="Download Assembly-CSharp.dll files"):
            try:
                r = requests.get("https://raw.githubusercontent.com/YeetDisDude/pixel-gun-3d/main/json/assembly-csharp.json", timeout=20)
                data = r.json()
                vers = list(data["versions"].keys())
            except Exception:
                vers = []
            dpg.add_combo(items=vers, default_value="Select Version", label="Version", tag="assemblyvercombo", width=150)
            dpg.add_button(label="Download", callback=downloadassembly)
            dpg.add_text("Status: ", tag="statustxt3")

        with dpg.collapsing_header(label="Make Unsearchable User Name"):
            dpg.add_input_text(width=150, label="Username", hint="Enter a Name", tag="username")
            dpg.add_text(" ")
            dpg.add_input_text(width=150, label="Output", readonly=True, tag="usernameoutput")
            dpg.add_button(label="Make Username", callback=makeusername)
            dpg.add_text("Status: ", tag="statustxt7")

        with dpg.collapsing_header(label="iOS Skin Plist Generator"):
            dpg.add_text("You can only use this once")
            items = ["YeetDisDude", "yeetdisdude", "ig: y_etd.sdude", "YeetDisDude#0001", "Subscribe", ".gg/wnr9ME7enQ", "byeguys gaming", "higuys gaming", "okand"]
            dpg.add_input_text(width=150, label="Base64", hint="Enter Base64", tag="skinb64")
            dpg.add_combo(label="Skin Name", default_value="Select A Skin Name", items=items, tag="skinname")
            dpg.add_button(label="Add", callback=skinplist)
            dpg.add_text("Status: idle", tag="statustxt8")

        with dpg.collapsing_header(label="Get All Scene Names"):
            dpg.add_button(label="Get list", callback=getallscenes)
            dpg.add_input_text(multiline=True, width=550, height=250, readonly=True, label="Scenes", tag="allscenes")


def tab2():
    with dpg.group():
        with dpg.collapsing_header(label="Spam Lightmap Contacts"):
            emails = ["mrbaest@gmail.com", "admin@fbi.gov", "niggerlover69@gmail.com", "admin@niggerprevention.org", "hermesis@nigga.gov", "higuys@yahoo.com", "byeguyshangout@nigga.gov", "blacklivesdoit@gmail.com"]
            dpg.add_input_text(hint="Enter Name", label="Name", tag="name", width=150)
            dpg.add_input_text(hint="Enter Message", label="Message", tag="message", width=150)
            dpg.add_combo(items=emails, default_value="Select an Email", tag="email", label="Email")
            dpg.add_input_text(hint="Enter threads", default_value="500", label="Threads", tag="threads", width=150)
            dpg.add_button(label="Spam", callback=lambda: spamcontacts())
            dpg.add_text("Status: Idle", tag="statustxt6")

        with dpg.collapsing_header(label="Update Player Logs"):
            items = ["Coins", "GemsCurrency", "BattlePassCurrency", "CraftCurrency", "ClanCurrency", "EventCurrency", "Coupons", "ClanSilver", "ClanLootBoxPoints", "Real", "Exp", "TankKeys", "RealCoin"]
            dpg.add_input_text(width=150, hint="Enter User ID", tag="userid", label="ID")
            dpg.add_combo(items=items, default_value="Select Currency", tag="currency", label="Currency")
            dpg.add_input_text(width=150, hint="Enter Amount", tag="amount", label="Amount")
            dpg.add_input_text(width=150, hint="Times to send", tag="times", label="Times")
            dpg.add_button(label="Update", callback=updateplayerlogs)
            dpg.add_text("Status: Idle", tag="statustxt")

        with dpg.collapsing_header(label="Check Ban"):
            dpg.add_input_text(hint="User ID", width=150, tag="usrid", label="ID")
            dpg.add_button(label="Check", callback=checkban)
            dpg.add_text("Status: ", tag="status_text")

        with dpg.collapsing_header(label="Get Currency Threshold"):
            dpg.add_text("Select an OS")
            dpg.add_combo(items=["iOS", "Android"], default_value="Android", tag="os", callback=currencythreshold)
            dpg.add_text("Coins: ", tag="coins")
            dpg.add_text("Gems: ", tag="gems")


def tab3():
    with dpg.group():
        with dpg.collapsing_header(label="Send Websocket A Message"):
            dpg.add_text("Warning: You will get IP Banned for 24h if you send unencrypted messages!")
            dpg.add_input_text(hint="Desired Message", width=300, tag="msg", label="Message")
            dpg.add_button(label="Connect & Send", callback=wsMain)
            dpg.add_text("Status: Idle (Waiting For Action)", tag="ws_status")
        with dpg.collapsing_header(label="Encrypt Message"):
            dpg.add_text("Coming soon")
        with dpg.collapsing_header(label="Decrypt Message"):
            dpg.add_text("Coming soon")


def tab4():
    with dpg.group():
        with dpg.collapsing_header(label="Find Weapon ID"):
            dpg.add_input_text(label="Search Term", hint="weapon name, gallery num etc", width=250, tag="wepsearchterm")
            dpg.add_button(label="Search", callback=searchwep)
            dpg.add_input_text(multiline=True, width=550, height=250, readonly=True, label="Result", tag="weaponidresult")

        with dpg.collapsing_header(label="Find Wear ID"):
            dpg.add_input_text(label="Search Term", hint="wear name", width=250, tag="wearsearchterm")
            dpg.add_button(label="Search", callback=searchwear)
            dpg.add_input_text(multiline=True, width=550, height=250, readonly=True, label="Result", tag="wearidresult")

        with dpg.collapsing_header(label="Find Item Record"):
            dpg.add_input_text(label="Search Term", hint="item record", width=250, tag="itemrecordsearchterm")
            dpg.add_button(label="Search", callback=searchitemrecord)
            dpg.add_input_text(multiline=True, width=550, height=250, readonly=True, label="Result", tag="itemrecordresult")

        with dpg.collapsing_header(label="Search Websocket Commands"):
            dpg.add_input_text(label="Search Term", hint="websocket command", width=250, tag="wscmdsearchterm")
            dpg.add_button(label="Search", callback=searchwscmd)
            dpg.add_input_text(multiline=True, width=550, height=250, readonly=True, label="Result", tag="wscmdresult")


def tabcredits():
    with dpg.group():
        dpg.add_text("Credits")
        dpg.add_text(" ")
        dpg.add_text("YeetDisDude#0001 - Creating The Script | github.com/YeetDisDude")
        dpg.add_text("Pulsed#1874 - Contributing (Websocket Message Sender) | github.com/ChrxnZ")
        dpg.add_text("TonicBoomerKewl - Item Record and Websocket Command JSON | github.com/TonicBoomerKewl")


def tabsettings():
    with dpg.group():
        dpg.add_text("Select a theme color (coming soon)")
        dpg.add_color_picker("Color Picker", width=200, display_hex=True, no_alpha=True, no_side_preview=True, callback=colorpicker)
        dpg.add_text(" ")
        dpg.add_button(label="Check Update", callback=check_update, width=150, height=35)
        dpg.add_text("Status: idle", tag="updatetxt")


def build_ui():
    dpg.create_context()

    with dpg.font_registry():
        font_path = ASSET_DIR / "SF-Pro-Display-Semibold.ttf"
        if font_path.exists():
            default_font = dpg.add_font(str(font_path), 20)
        else:
            default_font = None

    if default_font is not None:
        dpg.bind_font(default_font)

    with dpg.window(width=800, height=500, label=f"Pixel Gun 3D Tools | version {VERSION}", no_close=True, no_move=True, no_collapse=True, no_resize=True):
        with dpg.tab_bar():
            with dpg.tab(label="Tools"):
                tab1()
            with dpg.tab(label="API"):
                tab2()
            with dpg.tab(label="WebSocket"):
                tab3()
            with dpg.tab(label="Search"):
                tab4()
            with dpg.tab(label="Credits"):
                tabcredits()
            with dpg.tab(label="Settings"):
                tabsettings()

    dpg.create_viewport(title="Pixel Gun 3D Tools", width=816, height=538, resizable=False)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    build_ui()


if __name__ == "__main__":
    main()
