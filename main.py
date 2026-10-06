import json
import math
import random
import sys
from pathlib import Path

import pygame

# ------------------------------
# Game config
# ------------------------------
WIDTH, HEIGHT = 1200, 720
FPS = 60
WATER_TOP = 140

SKY = (131, 197, 255)
WATER = (24, 118, 189)
SAND = (214, 179, 110)
BOAT = (130, 92, 56)
LINE = (240, 240, 240)
TEXT = (255, 255, 255)
PANEL = (27, 42, 61)
ACCENT = (78, 205, 196)
GOOD = (95, 204, 120)
BAD = (212, 89, 89)

SAVE_DIR = Path("save")
SAVE_FILE = SAVE_DIR / "profile.json"

RODS = {
    "basic": {"name": "Basic Rod", "cost": 0, "power": 1.0, "speed": 1.0},
    "iron": {"name": "Iron Rod", "cost": 150, "power": 1.3, "speed": 1.1},
    "steel": {"name": "Steel Rod", "cost": 400, "power": 1.6, "speed": 1.25},
    "carbon": {"name": "Carbon Rod", "cost": 800, "power": 2.0, "speed": 1.5},
}

BAITS = {
    "worm": {"name": "Worm", "cost": 0, "attract": 1.0, "duration": 30},
    "cricket": {"name": "Cricket", "cost": 25, "attract": 1.3, "duration": 35},
    "minnow": {"name": "Minnow", "cost": 50, "attract": 1.6, "duration": 40},
    "shrimp": {"name": "Shrimp", "cost": 100, "attract": 2.0, "duration": 50},
}

HOOKS = {
    "small": {"name": "Small Hook", "cost": 0, "land_chance": 0.7},
    "med": {"name": "Medium Hook", "cost": 30, "land_chance": 0.85},
    "large": {"name": "Large Hook", "cost": 75, "land_chance": 0.95},
}

GEAR = {
    "net": {"name": "Net", "cost": 60, "land_bonus": 0.15},
    "gloves": {"name": "Fishing Gloves", "cost": 40, "land_bonus": 0.10},
}


def default_profile():
    return {
        "username": "Captain",
        "avatar_color": "#FFB27A",
        "avatar_style": 0,
        "coins": 0,
        "best_score": 0,
        "rod": "basic",
        "bait": "worm",
        "hook": "small",
        "gear": [],
    }


def load_profile():
    if not SAVE_FILE.exists():
        return default_profile()
    try:
        data = json.loads(SAVE_FILE.read_text())
        profile = default_profile()
        profile.update(data)
        return profile
    except Exception:
        return default_profile()


def save_profile(profile):
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    SAVE_FILE.write_text(json.dumps(profile, indent=2))


def clamp(value, low, high):
    return max(low, min(high, value))


def hex_to_rgb(hex_value):
    hex_value = hex_value.lstrip("#")
    if len(hex_value) == 3:
        hex_value = "".join(ch * 2 for ch in hex_value)
    return tuple(int(hex_value[i:i + 2], 16) for i in range(0, 6, 2))


def text_input_box(screen, rect, text, active):
    color = (255, 255, 255) if active else (200, 200, 200)
    pygame.draw.rect(screen, (30, 30, 30), rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, 2, border_radius=8)
    label = pygame.font.SysFont("arial", 20).render(text, True, (255, 255, 255))
    screen.blit(label, (rect.x + 14, rect.y + 8))


def draw_avatar_preview(screen, center, color_hex, style):
    color = hex_to_rgb(color_hex)
    x, y = center
    pygame.draw.circle(screen, color, (x, y), 32)

    if style == 0:
        pygame.draw.polygon(screen, (50, 50, 50), [(x - 18, y - 26), (x + 18, y - 26), (x + 8, y - 6), (x - 8, y - 6)])
    elif style == 1:
        pygame.draw.rect(screen, (79, 112, 255), (x - 16, y - 28, 32, 14), border_radius=6)
        pygame.draw.rect(screen, (79, 112, 255), (x - 10, y - 18, 20, 10), border_radius=5)
    elif style == 2:
        pygame.draw.rect(screen, (160, 90, 200), (x - 20, y - 30, 40, 10), border_radius=5)
        pygame.draw.rect(screen, (160, 90, 200), (x - 12, y - 42, 24, 18), border_radius=5)

    pygame.draw.circle(screen, (255, 255, 255), (x - 9, y - 3), 4)
    pygame.draw.circle(screen, (255, 255, 255), (x + 9, y - 3), 4)
    pygame.draw.circle(screen, (0, 0, 0), (x - 9, y - 3), 2)
    pygame.draw.circle(screen, (0, 0, 0), (x + 9, y - 3), 2)
    pygame.draw.arc(screen, (0, 0, 0), (x - 11, y + 4, 22, 10), 3.14, 6.28, 2)


def create_profile_screen():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Choose Your Fisher")
    clock = pygame.time.Clock()

    profile = default_profile()
    username = ""
    active_input = True
    color_index = 0
    style_index = 0
    palette = ["#FFB27A", "#7FD1B9", "#7AB6FF", "#F7D67A", "#D8B4F8", "#FF8A80"]
    styles = ["Classic", "Beanie", "Cool Hat"]

    font = pygame.font.SysFont("arial", 30)
    small = pygame.font.SysFont("arial", 20)

    running = True
    while running:
        screen.fill((14, 22, 34))

        title = font.render("Create Your Fisher", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        input_rect = pygame.Rect(WIDTH // 2 - 150, 120, 300, 50)
        text_input_box(screen, input_rect, username or "Enter username", active_input)

        preview_rect = pygame.Rect(120, 210, 720, 200)
        pygame.draw.rect(screen, PANEL, preview_rect, border_radius=18)
        draw_avatar_preview(screen, (WIDTH // 2, 285), palette[color_index], style_index)

        swatch_y = 440
        for i, color_hex in enumerate(palette):
            rect = pygame.Rect(150 + i * 110, swatch_y, 70, 40)
            pygame.draw.rect(screen, hex_to_rgb(color_hex), rect, border_radius=12)
            if i == color_index:
                pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=12)

        for i, style_name in enumerate(styles):
            rect = pygame.Rect(220 + i * 200, 500, 150, 38)
            color = (90, 130, 190) if i == style_index else (52, 72, 94)
            pygame.draw.rect(screen, color, rect, border_radius=12)
            label = small.render(style_name, True, (255, 255, 255))
            screen.blit(label, (rect.x + (rect.width - label.get_width()) // 2, rect.y + 8))

        prompt = small.render("Press ENTER to save and start fishing", True, (200, 220, 255))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 560))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    clean_name = username.strip() or "Captain"
                    profile["username"] = clean_name
                    profile["avatar_color"] = palette[color_index]
                    profile["avatar_style"] = style_index
                    save_profile(profile)
                    return profile

                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 14:
                    username += event.unicode
                elif event.key == pygame.K_TAB:
                    active_input = not active_input

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, _ in enumerate(palette):
                    rect = pygame.Rect(150 + i * 110, swatch_y, 70, 40)
                    if rect.collidepoint(mx, my):
                        color_index = i

                for i, _ in enumerate(styles):
                    rect = pygame.Rect(220 + i * 200, 500, 150, 38)
                    if rect.collidepoint(mx, my):
                        style_index = i


def create_fish(profile):
    rod_power = RODS[profile["rod"]]["power"]
    bait_attract = BAITS[profile["bait"]]["attract"]
    size = int(random.randint(24, 48) * (0.8 + rod_power * 0.3 + bait_attract * 0.2))
    size = clamp(size, 20, 80)

    base_value = random.randint(10, 50)
    value = int(base_value * (1.0 + (size - 24) / 60))

    return {
        "x": random.randint(80, WIDTH - 80),
        "y": random.randint(WATER_TOP + 60, HEIGHT - 100),
        "size": size,
        "vx": random.uniform(40, 90) * random.choice([-1, 1]),
        "value": value,
        "color": random.choice([(244, 95, 95), (106, 180, 111), (113, 164, 255), (255, 194, 102)]),
    }


def draw_fish(fish):
    x, y = fish["x"], fish["y"]
    size = fish["size"]
    body = pygame.Rect(x - size, y - size * 0.45, size * 2, size * 0.9)
    pygame.draw.ellipse(screen, fish["color"], body)

    tail_points = [
        (x - size - 8, y),
        (x - size - 15, y - size * 0.25),
        (x - size - 15, y + size * 0.25),
    ]
    pygame.draw.polygon(screen, fish["color"], tail_points)

    eye = (int(x + size * 0.45), int(y - size * 0.12))
    pygame.draw.circle(screen, (255, 255, 255), eye, 3)
    pygame.draw.circle(screen, (0, 0, 0), eye, 1)


def draw_boat(boat_x):
    hull = pygame.Rect(boat_x - 60, HEIGHT - 80, 120, 30)
    pygame.draw.rect(screen, BOAT, hull, border_radius=8)
    cabin = pygame.Rect(boat_x - 16, HEIGHT - 110, 32, 30)
    pygame.draw.rect(screen, (90, 64, 42), cabin, border_radius=6)
    pygame.draw.line(screen, (200, 200, 200), (boat_x + 12, HEIGHT - 110), (boat_x + 12, 50), 3)


def draw_bobber(bobber):
    if not bobber:
        return
    x, y = bobber["x"], bobber["y"]
    pygame.draw.circle(screen, (245, 214, 95), (int(x), int(y)), 9)
    pygame.draw.circle(screen, (180, 140, 45), (int(x), int(y)), 9, 2)


def draw_line(boat_x, bobber):
    if not bobber:
        return
    pygame.draw.line(screen, LINE, (boat_x + 12, 50), (bobber["x"], bobber["y"]), 2)


def draw_avatar(screen_target, x, y, color_hex, style, size=26):
    color = hex_to_rgb(color_hex)
    pygame.draw.circle(screen_target, color, (x, y), size)

    if style == 0:
        pygame.draw.polygon(screen_target, (52, 52, 52), [(x - 18, y - 18), (x + 18, y - 18), (x + 8, y - 2), (x - 8, y - 2)])
    elif style == 1:
        pygame.draw.rect(screen_target, (85, 112, 255), (x - 16, y - 22, 32, 12), border_radius=6)
    elif style == 2:
        pygame.draw.rect(screen_target, (168, 98, 212), (x - 18, y - 22, 36, 10), border_radius=6)
        pygame.draw.rect(screen_target, (168, 98, 212), (x - 10, y - 35, 20, 16), border_radius=5)

    pygame.draw.circle(screen_target, (255, 255, 255), (x - 9, y - 2), 4)
    pygame.draw.circle(screen_target, (255, 255, 255), (x + 9, y - 2), 4)
    pygame.draw.circle(screen_target, (0, 0, 0), (x - 9, y - 2), 2)
    pygame.draw.circle(screen_target, (0, 0, 0), (x + 9, y - 2), 2)
    pygame.draw.arc(screen_target, (0, 0, 0), (x - 11, y + 5, 22, 10), 3.14, 6.28, 2)


def show_inventory(profile):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Inventory & Shop")
    clock = pygame.time.Clock()

    font_lg = pygame.font.SysFont("arial", 32, bold=True)
    font_md = pygame.font.SysFont("arial", 24, bold=True)
    font_sm = pygame.font.SysFont("arial", 18)
    selected_tab = "rods"

    while True:
        screen.fill((14, 22, 34))

        title = font_lg.render("Inventory & Shop", True, TEXT)
        screen.blit(title, (40, 30))

        profile_text = font_sm.render(f"Coins: {profile['coins']}", True, ACCENT)
        screen.blit(profile_text, (WIDTH - 300, 40))

        tabs = ["rods", "baits", "hooks", "gear"]
        tab_y = 90
        for i, tab in enumerate(tabs):
            tab_name = tab.title()
            color = ACCENT if selected_tab == tab else (100, 100, 100)
            rect = pygame.Rect(40 + i * 220, tab_y, 200, 50)
            pygame.draw.rect(screen, color, rect, border_radius=8, width=2)
            text = font_sm.render(tab_name, True, color)
            screen.blit(text, (rect.x + 20, rect.y + 12))

            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if rect.collidepoint(mx, my):
                    selected_tab = tab

        content_rect = pygame.Rect(40, 160, WIDTH - 80, HEIGHT - 220)
        pygame.draw.rect(screen, PANEL, content_rect, border_radius=12)

        items = []
        if selected_tab == "rods":
            items = [(key, RODS[key]) for key in RODS]
            current = profile["rod"]
        elif selected_tab == "baits":
            items = [(key, BAITS[key]) for key in BAITS]
            current = profile["bait"]
        elif selected_tab == "hooks":
            items = [(key, HOOKS[key]) for key in HOOKS]
            current = profile["hook"]
        elif selected_tab == "gear":
            items = [(key, GEAR[key]) for key in GEAR]
            current = profile.get("gear", [])

        item_y = 180
        for key, item in items:
            item_rect = pygame.Rect(60, item_y, WIDTH - 120, 70)
            pygame.draw.rect(screen, (40, 55, 80), item_rect, border_radius=8)

            name = font_md.render(item["name"], True, TEXT)
            screen.blit(name, (80, item_y + 10))

            cost_text = font_sm.render(f"Cost: {item['cost']} coins", True, ACCENT if item["cost"] > 0 else GOOD)
            screen.blit(cost_text, (80, item_y + 40))

            if selected_tab == "gear":
                owned = key in current
            else:
                owned = key == current

            if owned:
                status = "EQUIPPED" if selected_tab != "gear" else "OWNED"
                status_text = font_sm.render(status, True, GOOD)
                screen.blit(status_text, (WIDTH - 200, item_y + 25))
            elif item["cost"] > 0:
                can_afford = profile["coins"] >= item["cost"]
                buy_color = GOOD if can_afford else BAD
                buy_text = font_sm.render("BUY", True, buy_color)
                screen.blit(buy_text, (WIDTH - 200, item_y + 25))

                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    if item_rect.collidepoint(mx, my) and can_afford:
                        profile["coins"] -= item["cost"]
                        if selected_tab == "gear":
                            if key not in profile["gear"]:
                                profile["gear"].append(key)
                        else:
                            if selected_tab == "rods":
                                profile["rod"] = key
                            elif selected_tab == "baits":
                                profile["bait"] = key
                            elif selected_tab == "hooks":
                                profile["hook"] = key
                        save_profile(profile)
                        pygame.time.wait(200)

            item_y += 90

        back_text = font_sm.render("Press E or ESC to return to fishing", True, (150, 150, 150))
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e, pygame.K_ESCAPE):
                    return


def run_game(profile):
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Harbor Hook")
    clock = pygame.time.Clock()

    boat_x = WIDTH // 2
    fish_list = [create_fish(profile) for _ in range(10)]
    score = 0
    bobber = None
    status = "Press C to cast your line | Press E for Inventory"
    state = "idle"
    cast_cooldown = 0
    save_counter = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        cast_cooldown -= dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                profile["best_score"] = max(profile["best_score"], score)
                save_profile(profile)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c and state == "idle" and cast_cooldown <= 0:
                    bobber = {"x": boat_x + 10, "y": 50, "mode": "dropping"}
                    state = "casting"
                    status = "Casting..."
                    cast_cooldown = 0.3

                if event.key == pygame.K_e:
                    show_inventory(profile)
                    status = "Press C to cast your line | Press E for Inventory"

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_w] or keys[pygame.K_UP]:
            boat_x -= 280 * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT] or keys[pygame.K_s] or keys[pygame.K_DOWN]:
            boat_x += 280 * dt

        boat_x = clamp(boat_x, 80, WIDTH - 80)

        for fish in fish_list:
            fish["x"] += fish["vx"] * dt
            if fish["x"] < 30 or fish["x"] > WIDTH - 30:
                fish["vx"] *= -1

        if bobber is not None:
            bobber["x"] = boat_x + 12

            if bobber["mode"] == "dropping":
                bobber["y"] += 240 * dt
                if bobber["y"] >= WATER_TOP + 200:
                    bobber["y"] = WATER_TOP + 200
                    bobber["mode"] = "waiting"
                    status = "Waiting for a bite..."

            elif bobber["mode"] == "waiting":
                for fish in fish_list:
                    distance = math.hypot(fish["x"] - bobber["x"], fish["y"] - bobber["y"])
                    if distance < fish["size"] * 0.6:
                        bobber["fish"] = fish
                        bobber["mode"] = "hooked"
                        status = f"Fish on! ({fish['value']} coins) Hold SPACE to reel!"
                        break

            elif bobber["mode"] == "hooked":
                fish = bobber["fish"]

                if keys[pygame.K_SPACE]:
                    rod_speed = RODS[profile["rod"]]["speed"]
                    bobber["y"] -= 260 * dt * rod_speed
                    fish["x"] += (bobber["x"] - fish["x"]) * 0.14
                    fish["y"] += (bobber["y"] - fish["y"]) * 0.14

                    if bobber["y"] <= 75:
                        hook_chance = HOOKS[profile["hook"]]["land_chance"]
                        gear_bonus = sum(GEAR[g]["land_bonus"] for g in profile.get("gear", []) if g in GEAR)
                        land_chance = clamp(hook_chance + gear_bonus, 0, 1.0)

                        if random.random() < land_chance:
                            score += fish["value"]
                            profile["coins"] += fish["value"]
                            profile["best_score"] = max(profile["best_score"], score)
                            fish_list.remove(fish)
                            bobber = None
                            state = "idle"
                            status = f"Caught! +{fish['value']} coins! Press C to cast again"
                            save_counter = 0
                            save_profile(profile)
                        else:
                            bobber = None
                            state = "idle"
                            status = "The fish broke free!"
                else:
                    fish["x"] += random.uniform(-50, 50) * dt
                    fish["y"] += random.uniform(-18, 18) * dt
                    bobber["y"] += 80 * dt
                    if bobber["y"] > HEIGHT - 70:
                        bobber = None
                        state = "idle"
                        status = "The fish got away..."

        save_counter += dt
        if save_counter > 5.0:
            profile["best_score"] = max(profile["best_score"], score)
            save_profile(profile)
            save_counter = 0

        if not fish_list:
            status = "You caught them all! Press R to reset the lake"
            if keys[pygame.K_r]:
                fish_list = [create_fish(profile) for _ in range(10)]
                score = 0
                bobber = None
                state = "idle"
                status = "Fresh lake! Press C to cast again"
                save_profile(profile)

        screen.fill(SKY)
        pygame.draw.rect(screen, SAND, (0, HEIGHT - 40, WIDTH, 40))

        pygame.draw.rect(screen, WATER, (0, WATER_TOP, WIDTH, HEIGHT - WATER_TOP))
        for i in range(0, WIDTH, 40):
            pygame.draw.line(screen, (90, 175, 220), (i, WATER_TOP), (i + 18, WATER_TOP + 12), 2)

        pygame.draw.circle(screen, (255, 224, 122), (WIDTH - 120, 80), 50)

        for fish in fish_list:
            draw_fish(fish)

        draw_boat(boat_x)
        draw_line(boat_x, bobber)
        draw_bobber(bobber)

        panel = pygame.Rect(20, 20, 300, 100)
        pygame.draw.rect(screen, PANEL, panel, border_radius=12)
        draw_avatar(screen, 60, 65, profile["avatar_color"], profile["avatar_style"], size=28)

        name_font = pygame.font.SysFont("arial", 24, bold=True)
        small_font = pygame.font.SysFont("arial", 16)
        name = name_font.render(profile["username"], True, TEXT)
        screen.blit(name, (100, 40))

        coins_text = small_font.render(f"Coins: {profile['coins']}", True, ACCENT)
        score_text = small_font.render(f"Score: {score}", True, TEXT)
        best_text = small_font.render(f"Best: {profile['best_score']}", True, TEXT)
        screen.blit(coins_text, (100, 65))
        screen.blit(score_text, (100, 82))
        screen.blit(best_text, (100, 99))

        equip_panel = pygame.Rect((WIDTH // 2) - 150, 20, 300, 100)
        pygame.draw.rect(screen, PANEL, equip_panel, border_radius=12)
        equip_font = pygame.font.SysFont("arial", 18, bold=True)
        eq_title = equip_font.render("Equipment", True, ACCENT)
        screen.blit(eq_title, (equip_panel.x + 20, equip_panel.y + 10))

        rod_text = small_font.render(f"Rod: {RODS[profile['rod']]['name']}", True, TEXT)
        bait_text = small_font.render(f"Bait: {BAITS[profile['bait']]['name']}", True, TEXT)
        hook_text = small_font.render(f"Hook: {HOOKS[profile['hook']]['name']}", True, TEXT)
        screen.blit(rod_text, (equip_panel.x + 20, equip_panel.y + 35))
        screen.blit(bait_text, (equip_panel.x + 20, equip_panel.y + 52))
        screen.blit(hook_text, (equip_panel.x + 20, equip_panel.y + 69))

        status_box = pygame.Rect(20, HEIGHT - 110, WIDTH - 40, 90)
        pygame.draw.rect(screen, PANEL, status_box, border_radius=12)
        status_lines = status.split(" | ")
        status_y = status_box.y + 15
        for line in status_lines:
            status_surf = small_font.render(line, True, TEXT)
            screen.blit(status_surf, (status_box.x + 20, status_y))
            status_y += 25

        help_text = small_font.render(
            "Controls: WASD/Arrow Keys to move | C to cast | SPACE to reel | E for Inventory",
            True,
            (150, 150, 150),
        )
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT - 35))

        pygame.display.flip()


def main():
    profile = load_profile()
    if not SAVE_FILE.exists():
        profile = create_profile_screen()
    else:
        profile = load_profile()

    run_game(profile)


if __name__ == "__main__":
    main()

