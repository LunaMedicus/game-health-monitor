import asyncio
import sys

sys.path.insert(0, "/Users/macabalitao/game-health-monitor/apps/api")

from src.database import SessionLocal
from src.services.steam import import_single_game

# 10 popular games to import as a starting batch
BATCH_IDS = [
    730,      # Counter-Strike 2
    440,      # Team Fortress 2
    570,      # Dota 2
    578080,   # PUBG: Battlegrounds
    381210,   # Dead by Daylight
    1172470,  # Apex Legends
    945360,   # Among Us
    1091500,  # Cyberpunk 2077
    1282730,  # Starfield
    105600,   # Terraria
]


async def main():
    db = SessionLocal()
    try:
        for app_id in BATCH_IDS:
            game = await import_single_game(db, app_id)
            if game:
                print(f"  Imported: {game.name} (steam_app_id={game.steam_app_id})")
            else:
                print(f"  Failed: app_id={app_id}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
