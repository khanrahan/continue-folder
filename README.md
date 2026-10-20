# Continue Folder

Plugin for [Autodesk Flame software](http://www.autodesk.com/products/flame).

Create a new reel on the Desktop and/or a system folder in MediaHub Files using tokens.

![screenshot](screenshot.png)

## Tokens

**Input Pattern** uses curly braces to interpret existing destination folders.
**Output Pattern** uses square brackets to form the new folder name.

**Input** (match / continue):
- `{PP}` / `{pp}` — AM/PM
- `{DD}` — Day
- `{hh}` / `{HH}` — Hour (12hr / 24hr)
- `{mm}` — Minute
- `{MM}` — Month
- `{YY}` / `{YYYY}` — Year
- `{version}` — Scan matching folders and continue the number sequence (*similar* to the version token for pattern browsing).

**Output** (new folder name):
- `[PP]` / `[pp]` — AM/PM
- `[DD]` — Day
- `[hh]` / `[HH]` — Hour (12hr / 24hr)
- `[mm]` — Minute
- `[MM]` — Month
- `[YY]` / `[YYYY]` — Year
- `[version]` — Next version from the input pattern scan. Optional hashes set zero-padding: `[version###]`.

Example: Input `{YYYY}_{MM}_v{version}` + Output `[YYYY]_[MM]_v[version###]` → `2026_08_v004`

## Example Workflow
You want to have a Library that will mirror a folder of exports on the server:
 1. Navigate to the filesystem folder of exports
 2. Select the folder `->` right click `->` Create... `->` Continue Folder
 3. Create a Desktop Reel that follows the preferred naming convention
 4. Copy your clips for export to this new Desktop Reel
 5. Drag this reel to the Library of exports
 6. Finally, drag the reel from the Library of exports into the MediaHub Files section to create a folder with the same name as the reel containing your clips

## Compatibility
|Release Version|Flame Version|
|---|---|
|v4.X.X|Flame 2025 and newer|
|v3.X.X|Flame 2025 and newer|
|v2.X.X|Flame 2022 up to 2024.2|
|v1.X.X|Flame 2021 up to 2021.2|

## Installation

### Flame 2025 and newer
The script is split across several modules, so copy all of the `continue_folder*.py` files together into the same folder.

To make available to all users on the workstation, copy the files to `/opt/Autodesk/shared/python/`

For specific users, copy the files to the appropriate path below...
|Platform|Path|
|---|---|
|Linux|`/home/<user_name>/flame/python/`|
|Mac|`/Users/<user_name>/Library/Preferences/Autodesk/flame/python/`|

### Flame 2023.3.2 up to 2024.2
To make available to all users on the workstation, copy `continue_folder.py` to `/opt/Autodesk/shared/python/`

For specific users, copy `continue_folder.py` to `/opt/Autodesk/user/<user name>/python/`

### Last Step
Finally, inside of Flame, go to Flame (fish) menu `->` Python `->` Rescan Python Hooks

## Menus
- Right-click a single selected folder in MediaHub Files `->` Create... `->` Continue Folder

## Acknowledgements
All the credit goes to Mike Vaglienty and his incredible PyFlame Library that he has very generously shared with us. You can find more information about the
library and its usage at the [Logik Portal](http://logik-portal.com/#pyflame/) or [Github](http://github.com/logik-portal/pyflame)
