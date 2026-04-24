from __future__ import annotations

import random
from abc import ABC, abstractmethod

from worldsim.models import DirectorBeat, Location, Npc, Player, World


LLM_ENGINE_CONTRACT = """
You are the world director, not the rules engine.

You may:
- name locations, NPCs, landmarks, factions, relics, rumors
- frame scenes and present opportunities
- suggest a check, risk, or consequence using structured intent

You may not:
- decide dice outcomes
- modify HP, gold, XP, inventory, or map coordinates
- invalidate the established world state

Return structured beats with:
- title
- narration
- mechanical_request
- difficulty
- tags
- follow_up_hook
""".strip()


class Director(ABC):
    @abstractmethod
    def introduce_world(self, world: World, player: Player, memory_context: list[str] | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def describe_location(
        self,
        world: World,
        player: Player,
        location: Location | None,
        npc: Npc | None,
        memory_context: list[str] | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def respond_to_action(
        self,
        world: World,
        player: Player,
        action: str,
        location: Location | None,
        npc: Npc | None,
        memory_context: list[str] | None = None,
    ) -> DirectorBeat:
        raise NotImplementedError

    @abstractmethod
    def ambient_world_event(self, world: World) -> str:
        raise NotImplementedError


class MockDirector(Director):
    """Template-driven director used until a real LLM backend is wired in."""

    def __init__(self, seed: int) -> None:
        self.random = random.Random(seed)

    def introduce_world(self, world: World, player: Player, memory_context: list[str] | None = None) -> str:
        start = next(location for location in world.locations if location.position == player.position)
        openings = [
            f"{player.name} of {player.homeland} arrives in {start.name}, where rumors travel faster than carts.",
            f"The road ends at {start.name}. Beyond it, the frontier begins writing new history around {player.name}.",
            f"{player.name} steps into {start.name} as if the world has been waiting for the right witness.",
        ]
        intro = self.random.choice(openings)
        if memory_context:
            intro += f" Memory already anchors the scene: {memory_context[0]}"
        return intro

    def describe_location(
        self,
        world: World,
        player: Player,
        location: Location | None,
        npc: Npc | None,
        memory_context: list[str] | None = None,
    ) -> str:
        if location is None:
            text = "The wilderness is quiet here, but not empty. Tracks and weather argue over which story matters most."
            if memory_context:
                text += f" A remembered thread returns: {memory_context[0]}"
            return text

        details = [
            f"{location.name} sits in the {location.biome.value.lower()}, carrying an air of {location.summary.lower()}",
            f"{location.name} feels lived in and watched. The ground suggests old traffic and newer caution.",
            f"{location.name} is the sort of place where news arrives bent out of shape but still dangerous.",
        ]
        note = self.random.choice(details)
        if npc is not None:
            note += f" {npc.name}, a {npc.disposition} {npc.role}, is nearby."
        if memory_context:
            note += f" You recall: {memory_context[0]}"
        return note

    def respond_to_action(
        self,
        world: World,
        player: Player,
        action: str,
        location: Location | None,
        npc: Npc | None,
        memory_context: list[str] | None = None,
    ) -> DirectorBeat:
        memory_line = f" Memory leans on the moment: {memory_context[0]}" if memory_context else ""
        if action == "explore":
            title = "Field Discovery"
            place = location.name if location else "the wilds"
            narrations = [
                f"While exploring {place}, you find the edge of a story larger than the road itself.",
                f"The land around {place} yields a small secret, as if it expected someone patient enough to notice.",
                f"A detail hidden in plain sight around {place} begins to look deliberate.",
            ]
            hooks = [
                "Fresh boot prints lead away from the scene.",
                "Someone marked the stones with a half-erased sigil.",
                "The clue points toward a larger power moving quietly nearby.",
            ]
            return DirectorBeat(
                title=title,
                narration=self.random.choice(narrations) + memory_line,
                mechanical_request="exploration_check",
                difficulty=9 + (location.danger if location else 2),
                tags=["exploration", "discovery"],
                follow_up_hook=self.random.choice(hooks),
            )

        if action == "talk":
            title = "Conversation"
            if npc is None:
                return DirectorBeat(
                    title=title,
                    narration="You call into the air, but the frontier answers with weather and distance." + memory_line,
                    mechanical_request=None,
                    tags=["social", "quiet"],
                )
            rumors = [
                f"{npc.name} hints that merchants have started avoiding one of the old roads.",
                f"{npc.name} mentions lights moving where no village stands.",
                f"{npc.name} swears an oath was broken somewhere upriver, and the land remembers.",
            ]
            return DirectorBeat(
                title=title,
                narration=self.random.choice(rumors) + memory_line,
                mechanical_request="social_check",
                difficulty=8,
                tags=["social", "rumor"],
                follow_up_hook=f"{npc.name} might know more if you prove useful.",
            )

        if action == "attack":
            return DirectorBeat(
                title="Violence",
                narration="Steel settles the question that words left unresolved." + memory_line,
                mechanical_request="combat_check",
                difficulty=10 + (location.danger if location else 3),
                tags=["combat"],
                follow_up_hook="Victory here will reshape how this place speaks about you.",
            )

        if action == "rest":
            return DirectorBeat(
                title="Camp",
                narration="You take a careful pause, listening for the difference between silence and danger." + memory_line,
                mechanical_request=None,
                tags=["rest"],
            )

        return DirectorBeat(
            title="Passing Time",
            narration="The world keeps moving, whether watched closely or not." + memory_line,
            mechanical_request=None,
            tags=["time"],
        )

    def ambient_world_event(self, world: World) -> str:
        subjects = [location.name for location in world.locations[:4]]
        templates = [
            f"A trader from {self.random.choice(subjects)} claims the river route is safer this week.",
            f"Smoke was seen near {self.random.choice(subjects)} after sunset.",
            f"Two households in {self.random.choice(subjects)} are feuding over a debt no one can verify.",
            f"An old banner has been raised again near {self.random.choice(subjects)}.",
        ]
        return self.random.choice(templates)
