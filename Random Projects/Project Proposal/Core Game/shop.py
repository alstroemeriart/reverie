# SHOP

from ui import typewriter, clear_screen
from items import (
    HealingPotion, AttackBoost, HintPotion,
    DefenseBoost, MegaHealingPotion, SpeedBoost,
    PoisonBomb, FreezeScroll, WeaknessCurse,
    DoubleGoldCharm, RevivalStone, AllItems
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


def get_merchant_greeting(player):
    if player.streak >= 10:
        return "\"Ah, a scholar of great wisdom! I'll give you my finest.\""
    elif player.hp < player.max_hp * 0.3:
        return "\"You look terrible. Buy something before you die.\""
    elif player.gold > 100:
        return "\"A wealthy traveler! Everything's full price for you.\""
    else:
        return "\"Welcome, wanderer. Browse at your leisure.\""


def _build_stock(player):
    """
    Generate the shop's stock for one visit.
    Returns a list of slot dicts. Called once per shop visit.
    """
    stock = []

    # Pick 5 normal items
    num_items = min(5, len(ITEM_POOL))
    selected_classes = random.sample(ITEM_POOL, k=num_items)

    for item_class in selected_classes:
        base_price = random.randint(30, 120)
        final_price = player.shop_discount(base_price)
        stock.append({
            "item": item_class(),
            "price": final_price,
            "sold": False,
            "mystery": False,
        })

    # Add exactly one mystery slot at a slight discount
    mystery_class = random.choice(ITEM_POOL)
    mystery_instance = mystery_class()
    base_mystery_price = random.randint(15, 60)
    mystery_price = int(player.shop_discount(base_mystery_price) * 0.8)
    stock.append({
        "item": mystery_instance,
        "price": max(5, mystery_price),
        "sold": False,
        "mystery": True,
    })

    return stock


def _get_rarity(item_instance):
    """Look up an item's rarity string from AllItems."""
    for entry in AllItems:
        if isinstance(item_instance, entry["class"]):
            return entry["rarity"]
    return "unknown"


def _display_stock(stock, player):
    """
    Print the current shop stock and return slot_map,
    sell_num, and leave_num for input handling.
    """
    clear_screen()
    typewriter("\n=== Welcome to the Shop ===")
    typewriter(f"HP:   {player.hp}/{player.max_hp}")
    typewriter(f"Gold: {player.gold}")
    time.sleep(0.3)

    typewriter("\nItems for sale:")
    slot_map = {}
    display_num = 1

    for i, slot in enumerate(stock):
        if slot["sold"]:
            if slot["mystery"]:
                typewriter(f"  -. ??? — SOLD OUT")
            else:
                typewriter(f"  -. {slot['item'].name} — SOLD OUT")

        elif slot["mystery"]:
            rarity = _get_rarity(slot["item"])
            typewriter(f"  {display_num}. ??? [{rarity}] — {slot['price']} gold  (mystery item)")
            slot_map[display_num] = i
            display_num += 1

        else:
            desc = getattr(slot["item"], "description", "")
            typewriter(f"  {display_num}. {slot['item'].name} — {slot['price']} gold")
            if desc:
                typewriter(f"      {desc}")
            slot_map[display_num] = i
            display_num += 1

    sell_num = display_num
    leave_num = display_num + 1
    typewriter(f"  {sell_num}. Sell an item")
    typewriter(f"  {leave_num}. Leave shop")

    return slot_map, sell_num, leave_num


def shop(player):
    """Roguelite shop with fixed stock per visit that depletes as items are bought."""

    typewriter(get_merchant_greeting(player))
    time.sleep(0.5)

    # Build stock once for the entire visit
    stock = _build_stock(player)

    while True:

        # Check if everything is sold out before displaying
        available = [s for s in stock if not s["sold"]]
        if not available:
            clear_screen()
            typewriter("\nThe merchant shrugs. \"Sold out — come back next time.\"")
            time.sleep(1.5)
            return

        slot_map, sell_num, leave_num = _display_stock(stock, player)

        choice = input("\n> ").strip()
        try:
            choice = int(choice)
        except ValueError:
            typewriter("Invalid choice.")
            time.sleep(0.5)
            continue

        if choice == leave_num:
            typewriter("Leaving shop...")
            time.sleep(0.5)
            return

        if choice == sell_num:
            _sell_item(player)
            continue

        if choice in slot_map:
            stock_index = slot_map[choice]
            slot = stock[stock_index]

            if player.gold >= slot["price"]:
                player.gold -= slot["price"]
                player.inventory.append(slot["item"])
                slot["sold"] = True

                if slot["mystery"]:
                    typewriter(f"You unwrap the mystery item...")
                    time.sleep(0.8)
                    typewriter(f"It's a {slot['item'].name}!")
                    desc = getattr(slot["item"], "description", "")
                    if desc:
                        typewriter(f"  {desc}")
                else:
                    typewriter(f"You bought {slot['item'].name}!")

                typewriter(f"Gold remaining: {player.gold}")
                time.sleep(0.5)
            else:
                typewriter("Not enough gold!")
                time.sleep(0.5)

        else:
            typewriter("Invalid choice.")
            time.sleep(0.5)


def _sell_item(player):
    """Let the player sell an item from their inventory for half its price."""
    if not player.inventory:
        typewriter("You have nothing to sell.")
        return

    typewriter("\nYour inventory (sell for half price):")
    for i, item in enumerate(player.inventory, 1):
        sell_price = item.price // 2
        desc = getattr(item, "description", "")
        typewriter(f"  {i}. {item.name} — sells for {sell_price} gold")
        if desc:
            typewriter(f"      {desc}")
    typewriter(f"  {len(player.inventory) + 1}. Cancel")

    try:
        choice = int(input("> ").strip())
    except ValueError:
        typewriter("Invalid choice.")
        return

    if choice == len(player.inventory) + 1:
        typewriter("Cancelled.")
        return

    if 1 <= choice <= len(player.inventory):
        item = player.inventory.pop(choice - 1)
        sell_price = item.price // 2
        player.gold += sell_price
        typewriter(f"Sold {item.name} for {sell_price} gold.")
        typewriter(f"Gold: {player.gold}")
    else:
        typewriter("Invalid choice.")

