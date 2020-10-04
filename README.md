# Foundry VTT Journal Export 1.0
Python script for exporting Journal entries from Foundry VTT, it will create proper directory hierarchy and copy used image assets.

## Requirements
 - Python 3.x

## Usage
This script can be launched from any location, you will need to give it proper relative path to the direcotry containing your world files.
```bash
python3 journal_export.py -world PATH_TO_WORLD_DIRECTORY [--sorted]
eg. python3 journal_export.py -world \Data\worlds\test-world
```

This will export all Journal Entries with default permission set to Observer or higher into `Journal export/world_name` directory:
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

You can enable sorting of directories and entries by name by adding `sorted` flag:
```bash
python3 journal_export.py -world \Data\worlds\test-world --sorted
```

## Known issues/future plans
- Maintaning issues with new Foundry versions
- Resolving reproted issues
