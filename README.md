# Harbor Hook

A simple fishing game with:
- username + avatar creation
- persistent save file for each player
- coin rewards from bigger fish
- shop system for rods, bait, hooks, and gear
- inventory screen with upgrades

## Setup

1. Install Python 3.9+
2. Install dependencies:
   pip install -r requirements.txt
3. Run the game:
   python main.py

## Controls
- WASD or Arrow Keys: move the boat
- C: cast the line
- Space: reel in the fish
- E: open inventory and shop
- R: reset the lake after all fish are caught

## Save system
Your profile is stored in `save/profile.json`, so the username, avatar, coins, and upgrades load every time you run the game again.
