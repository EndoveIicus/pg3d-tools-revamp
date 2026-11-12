<h1 align="center">Pixel Gun 3D Tools Revamped</h1>
<p align="center">A Python utility suite for Pixel Gun 3D modding, reverse engineering, and experimentation.</p>
<p align="center">Maintained by <strong>EndoveIicus</strong> · Current Version: <strong>0.1.0</strong></p>

<p align="center">
  <a href="https://github.com/EndoveIicus/pg3d-tools/releases"><img src="https://img.shields.io/github/downloads/EndoveIicus/pg3d-tools/total.svg" alt="GitHub Downloads"></a>
  <a href="https://discord.gg/wnr9ME7enQ"><img src="https://img.shields.io/discord/1082866190097072158" alt="Discord"></a>
  <a href="https://github.com/EndoveIicus/pg3d-tools/releases"><img src="https://img.shields.io/github/v/release/EndoveIicus/pg3d-tools" alt="Release Version"></a>
</p>
<p align="center">
  <a href="https://github.com/EndoveIicus/pg3d-tools/stargazers"><img src="https://img.shields.io/github/stars/EndoveIicus/pg3d-tools?style=social" alt="GitHub Stars"></a>
</p>

[![HitCount](https://hits.dwyl.com/EndoveIicus/pg3d-tools.svg?style=flat-square)](https://github.com/EndoveIicus/pg3d-tools)

# Where to download
You can choose between a lightweight CLI version and a more visual GUI version, depending on how you want to work with the tools.

CLI: https://github.com/EndoveIicus/pg3d-tools/tree/main/cli/src

GUI: https://github.com/EndoveIicus/pg3d-tools/tree/main/gui/src

# Usage
1. Download the latest release from the releases tab or clone the repository.
2. Run the executable, or execute `py pg3dtools.py` if you're using the Python script directly.
3. If dependencies are missing, the script will install them automatically for you.

It is recommended to use the New Terminal from the Microsoft Store: [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)

# To do (Features)
- Dump (coming soon)
  - Cpp2IL dump [gui]
  - Il2Cpp dump [gui]
- Settings
  - Set PG3D Tools theme color (currently being improved)

# Features
- Check ban
  - Check whether an ID is banned from PG3D
- Download Dump.cs Files
  - Download PG3D's Dump.cs files (IL2CPP-based)
- Download Assembly-CSharp.dll
  - Download assembly files with automatic updates as new versions are released
- Get cheater currency threshold
  - Display the current (outdated) currency threshold used by PG3D servers
- Update player logs
  - Choose the currency type and ID to update in a player's logs without actually adding currency
- Spam lightmap contacts
  - Send messages to Lightmap contacts using threading support
- iOS Skin plist generator
  - Generate modded iOS skin files for advanced customization
- Get all scene names
  - Retrieve all scene names from the game
- Send Websocket Message
  - Send messages through Pixel Gun 3D's WebSocket connection
  - Warning: sending unencrypted messages may result in an IP ban
- Find Weapon ID
  - Search through all weapon IDs and related entries
- Find Wear ID
  - Search for wear IDs
- Find Item Record
  - Search for a specific item's Item Record
- Search Websocket command
  - Search the available PG3D WebSocket commands

# Preview
![Image1](/image/1gui.png)
![Image2](/image/2gui.png)
![Image3](/image/3gui.png)

# Credits
- [YeetDisDude](https://github.com/YeetDisDude) - Original Creator
- [TonicBoomerKewl](https://github.com/TonicBoomerKewl) - for the Item Record and WebSocket command JSON
- [Pulsed](https://github.com/ChrxnZ) - for the WebSocket communication feature

