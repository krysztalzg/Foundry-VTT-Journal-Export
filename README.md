# Foundry VTT Journal Export 0.1
Python script for exporting Journal entries from Foundry VTT, it will create proper directory hierarchy and copy used image assets.

## Usage
This script can be launched from any location, you will need to give it proper relative path to the direcotry containing your world files.
```bash
python journal_export.py -world PATH_TO_WORLD_DIRECTORY
eg. python journal_export.py -world \Data\worlds\test-world
```
This will export all Journal Entries with default permission set to Observer or higher into `Journal export/world_name directory`:
```
.
├─ journal_export.py
└─ Journal Export
   ├─ NPCs
   │  └─ BBEG.md
   ├─ Cities
   │  ├─ Waterdeep.md
   │  └─ BBEG.md
   └─ Message from friend.md
```
