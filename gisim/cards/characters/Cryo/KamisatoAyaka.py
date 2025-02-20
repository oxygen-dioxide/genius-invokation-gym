"""神里绫华"""

from queue import PriorityQueue
from typing import TYPE_CHECKING, Dict, List, cast

from gisim.cards.base import TalentCard
from gisim.cards.characters.base import CharacterCard, CharacterSkill, GenericSkill
from gisim.classes.enums import (
    CharPos,
    ElementType,
    EntityType,
    EquipmentType,
    Nation,
    PlayerID,
    SkillType,
    WeaponType,
)
from gisim.classes.equipment import TalentEntity
from gisim.classes.message import (
    ChangeCharacterMsg,
    DealDamageMsg,
    GenerateCharacterStatusMsg,
    GenerateEquipmentMsg,
    Message,
    PayChangeCharacterCostMsg,
    RoundEndMsg,
    UseCardMsg,
)
from gisim.classes.summon import AttackSummon, Summon
from gisim.env import INF_INT

if TYPE_CHECKING:
    from gisim.classes.character import CharacterEntity
    from gisim.game import GameInfo


class KamisatoArtKabuki(GenericSkill):
    """
    神里流·倾
    ~~~~~~~~
    `普通攻击` 造成2点`物理伤害`。
    """

    id: int = 11051
    name: str = "Kamisato Art: Kabuki"
    text: str = """
    Deals 2 Physical DMG.
    """
    costs: Dict[ElementType, int] = {ElementType.CRYO: 1, ElementType.ANY: 2}
    type: SkillType = SkillType.NORMAL_ATTACK
    damage_element: ElementType = ElementType.NONE
    damage_value: int = 2


class KamisatoArtHyouka(GenericSkill):
    """
    神里流·冰华
    ~~~~~~~~~~
    `元素战技`造成3点`冰元素伤害`。
    """

    id: int = 11052
    name: str = "Kamisato Art: Hyouka"
    text: str = """
    Deals 3 Cryo DMG
    """
    costs: Dict[ElementType, int] = {ElementType.CRYO: 3}
    type: SkillType = SkillType.ELEMENTAL_SKILL
    damage_element: ElementType = ElementType.CRYO
    damage_value: int = 3


class KamisatoArtSoumetsu(GenericSkill):
    """
    神里流·霜灭
    ~~~~~~~~~~
    `元素爆发`造成4点`冰元素伤害`，召唤`霜见雪关扉`。
    """

    id: int = 11053
    name: str = "Kamisato Art: Soumetsu"
    text: str = """
    Deals 4 Cryo DMG, summons 1 Frostflake Seki no To.
    """
    costs: Dict[ElementType, int] = {ElementType.CRYO: 3, ElementType.POWER: 3}
    type: SkillType = SkillType.ELEMENTAL_BURST
    damage_element: ElementType = ElementType.CRYO
    damage_value: int = 4
    summon_name: str = "Frostflake Seki no To"


class KamisatoArtSenho(CharacterSkill):
    """
    神里流·霰步
    ~~~~~~~~~
    `被动技能`当此角色被切换为`出战角色`时，附属`冰元素附魔`。
    """

    id: int = 11054
    name: str = "Kamisato Art: Senho"
    text: str = """
    (Passive) When switched to be the active character, this character gains Cryo Elemental Infusion.
    """
    costs: Dict[ElementType, int] = {}
    type: SkillType = SkillType.PASSIVE_SKILL

    def use_skill(
        self,
        msg_queue: PriorityQueue,
        parent: "CharacterEntity",
    ):
        top_msg = msg_queue.queue[0]
        updated = False
        if isinstance(top_msg, ChangeCharacterMsg):
            top_msg = cast(ChangeCharacterMsg, top_msg)
            if top_msg.target == (parent.player_id, parent.position):
                new_msg = GenerateCharacterStatusMsg(
                    sender_id=parent.player_id,
                    status_name="Cryo Infusion",
                    target=(parent.player_id, parent.position),
                    remaining_round=1,
                    remaining_usage=INF_INT,
                )
                msg_queue.put(new_msg)
                updated = True

        return updated


class KamisatoAyaka(CharacterCard):
    """神里凌华"""

    id: int = 1105
    name: str = "Kamisato Ayaka"
    element_type: ElementType = ElementType.CRYO
    nations: List[Nation] = [Nation.Inazuma]
    health_point: int = 10
    power: int = 0
    max_power: int = 3
    weapon_type: WeaponType = WeaponType.SWORD
    skills: List[CharacterSkill] = [
        KamisatoArtKabuki(),
        KamisatoArtHyouka(),
        KamisatoArtSoumetsu(),
        KamisatoArtSenho(),
    ]


class FrostflakeSekinoTo(AttackSummon):
    """
    霜见雪关扉
    ~~~~~~~~~
    `召唤物`在结束阶段造成两点`冰元素伤害`，该召唤物可以被使用两次。
    """

    name: str = "Frostflake Seki no To"
    usages: int = 2
    damage_element: ElementType = ElementType.CRYO
    damage_value: int = 2


class KantenSenmyouBlessingCard(TalentCard):
    id = 211051
    name = "Kanten Senmyou Blessing"
    character_name: str = "Kamisato Ayaka"
    costs: Dict[ElementType, int] = {ElementType.CRYO: 2}
    text: str = """
    The Cryo Elemental Infusion created by your Kamisato Ayaka, who has this card equipped, allows the character to which it is attached to deal +1 Cryo DMG.
    When you switch to Kamisato Ayaka, who has this card equipped: Spend 1 less Elemental Die. (Once per Round)
    (You must have Kamisato Ayaka in your deck to add this card to your deck.)
    """

    def use_card(
        self,
        msg_queue: PriorityQueue,
        game_info: "GameInfo",
    ):
        top_msg = msg_queue.queue[0]
        top_msg = cast(UseCardMsg, top_msg)
        player_id, entity_type, idx = top_msg.card_target[0]
        char_pos = CharPos(idx)
        new_msg = GenerateEquipmentMsg(
            sender_id=player_id,
            target=(player_id, char_pos),
            equipment_name=self.name,
            equipment_type=EquipmentType.TALENT,
        )
        msg_queue.put(new_msg)


class KantenSenmyouBlessing(TalentEntity):
    name: str = "Kanten Senmyou Blessing"

    def msg_handler(self, msg_queue: PriorityQueue) -> bool:
        top_msg = msg_queue.queue[0]
        updated = False
        if self._uuid in top_msg.responded_entities:
            return False

        if isinstance(top_msg, PayChangeCharacterCostMsg):
            # 切凌华花费 -1
            top_msg = cast(PayChangeCharacterCostMsg, top_msg)
            if (
                self.active
                and top_msg.sender_id == self.player_id
                and top_msg.target_pos == self.char_pos
            ) and top_msg.required_cost[ElementType.ANY] > 0:
                top_msg.required_cost[ElementType.ANY] -= 1
                updated = True
                if not top_msg.simulate:
                    self.active = False
                    self.triggered_in_a_round = 1

        elif isinstance(top_msg, RoundEndMsg):
            top_msg = cast(RoundEndMsg, top_msg)
            self.active = True
            self.triggered_in_a_round = 0
            updated = True

        elif isinstance(top_msg, DealDamageMsg):
            # 造成的冰元素伤害 + 1
            top_msg = cast(DealDamageMsg, top_msg)
            if (
                top_msg.attacker == (self.player_id, self.char_pos)
                and top_msg.targets[0][2] == ElementType.CRYO
            ):
                top_msg.targets[0] = (
                    top_msg.targets[0][0],
                    top_msg.targets[0][1],
                    top_msg.targets[0][2],
                    top_msg.targets[0][3] + 1,
                )
                updated = True

        if updated:
            top_msg.responded_entities.append(self._uuid)

        return updated
