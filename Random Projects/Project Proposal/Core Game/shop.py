# shop.py
from ui import typewriter
from aid import (
    HealingPotion, AttackBoost, HintPotion,
    DefenseBoost, MegaHealingPotion, SpeedBoost,
    PoisonBomb, FreezeScroll, WeaknessCurse,
    DoubleGoldCharm, RevivalStone
)
import random, time

# Full aid pool (can expand further later)
ITEM_POOL = [
    HealingPotion,
    AttackBoost,
    HintPotion,
    DefenseBoost,
    MegaHealingPotion, 
    SpeedBoost,
    PoisonBomb,
    FreezeScroll,
    WeaknessCurse,
    DoubleGoldCharm,
    RevivalStone
]

def shop(player):
    """Roguelite shop with 5 random aid per visit."""
    while True:
        typewriter("\n=== Welcome to the Shop ===")
        typewriter(f"Gold: {player.gold}")
        time.sleep(0.5)

        # Randomly select 5 aid to sell this visit
        items_for_sale = random.sample(ITEM_POOL, k=min(5, len(ITEM_POOL)))
        item_slots = []

        for i, item_class in enumerate(items_for_sale, 1):
            # Random base price for rarity scaling
            base_price = random.randint(30, 120)
            final_price = player.shop_discount(base_price)
            item_instance = item_class()  # instantiate
            item_slots.append((item_instance, final_price))
            typewriter(f"{i}. {item_instance.name} - {final_price} gold")
            time.sleep(0.2)

        typewriter(f"{len(item_slots)+1}. Leave Shop")

        choice = input("> ").strip()
        try:
            choice = int(choice)
        except:
            typewriter("Invalid choice.")
            continue

        if choice == len(item_slots)+1:
            typewriter("Leaving shop...")
            return  # exit shop

        if 1 <= choice <= len(item_slots):
            aid, price = item_slots[choice-1]
            final_price = player.shop_discount(price)

            if player.gold >= final_price:
                player.gold -= final_price
                player.inventory.append(aid)
                typewriter(f"You bought {aid.name}!")
                typewriter(f"Gold remaining: {player.gold}")
                time.sleep(0.5)
            else:
                typewriter("Not enough gold!")
                time.sleep(0.5)
        else:
            typewriter("Invalid choice.")
            time.sleep(0.5)