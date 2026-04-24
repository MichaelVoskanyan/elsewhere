from __future__ import annotations

from pathlib import Path

from worldsim.engine import WorldEngine
from worldsim.memory import CampaignStore
from worldsim.tui import WorldSimApp


class Game:
    def __init__(self) -> None:
        save_path = Path(__file__).resolve().parent.parent / "data" / "campaign.json"
        self.store = CampaignStore(save_path)
        self.engine = WorldEngine()

    def run(self) -> None:
        WorldSimApp(store=self.store, engine=self.engine).run()
