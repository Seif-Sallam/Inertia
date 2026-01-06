import pygame
import math
import random
import sys
import pygame.gfxdraw

pygame.init()

TILE_SIZE = 48
GRID_W, GRID_H = 10, 10
WIDTH = GRID_W * TILE_SIZE
HEIGHT = GRID_H * TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Inertia")

clock = pygame.time.Clock()

LEVEL = [
    "..#..#....",
    ".G.#.##.B.",
    "..##...##.",
    ".S..##....",
    ".###.#####",
    "..G..P..G.",
    "...##..#..",
    ".B..##..G.",
    "..G..##..G",
    "....#.....",
]

assert len(LEVEL) == GRID_H and all(len(r) == GRID_W for r in LEVEL)

grid = [list(row) for row in LEVEL]

def find_player():
    for y in range(GRID_H):
        for x in range(GRID_W):
            if grid[y][x] == 'P':
                grid[y][x] = '.'
                return x, y
    return 1, 1

player_tile_x, player_tile_y = find_player()
player_pos = [player_tile_x * TILE_SIZE + TILE_SIZE // 2, player_tile_y * TILE_SIZE + TILE_SIZE // 2]
moving = False
move_target = [0, 0]
move_dir = (0, 0)
move_speed = 6.0

dirs8 = [
    (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)
]

gems_collected = 0
game_over = False
game_won = False
total_gems = sum(row.count('G') for row in LEVEL)

# Particles for polish effects
class Particle:
    def __init__(self, pos, vel, color, life, radius):
        self.pos = list(pos)
        self.vel = list(vel)
        self.color = color
        self.life = life
        self.max_life = life
        self.radius = radius

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[1] += 0.15  # gravity subtle
        self.life -= 1

    def draw(self, surf):
        a = max(0, int(255 * (self.life / self.max_life)))
        col = (self.color[0], self.color[1], self.color[2], a)
        s = pygame.Surface((self.radius * 2 + 2, self.radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (self.radius + 1, self.radius + 1), self.radius)
        surf.blit(s, (self.pos[0] - self.radius, self.pos[1] - self.radius))

particles = []

def tile_in_bounds(x, y):
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def draw_vertical_gradient(surf, color_top, color_bottom):
    w, h = surf.get_size()
    for i in range(h):
        t = i / (h - 1)
        col = (
            int(color_top[0] * (1 - t) + color_bottom[0] * t),
            int(color_top[1] * (1 - t) + color_bottom[1] * t),
            int(color_top[2] * (1 - t) + color_bottom[2] * t),
        )
        pygame.draw.line(surf, col, (0, i), (w, i))


def draw_glossy_circle(surf, pos, radius, base_color, rim_color=(255,255,255)):
    # draw shadow/gloss by concentric circles
    x, y = int(pos[0]), int(pos[1])
    layers = max(6, radius // 3)
    for i in range(layers, 0, -1):
        r = int(radius * (i / layers))
        alpha = int(200 * (i / layers))
        col = (base_color[0], base_color[1], base_color[2], alpha)
        s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(s, r+1, r+1, r, col)
        surf.blit(s, (x - r - 1, y - r - 1))
    # rim highlight
    rim = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.gfxdraw.filled_circle(rim, radius, radius, int(radius*0.6), (255,255,255,80))
    surf.blit(rim, (x-radius, y-radius), special_flags=pygame.BLEND_ADD)


def draw_glossy_gem(surf, tilex, tiley):
    cx = tilex * TILE_SIZE + TILE_SIZE // 2
    cy = tiley * TILE_SIZE + TILE_SIZE // 2
    r = TILE_SIZE // 4
    # base diamond
    pts = [
        (cx, cy - r),
        (cx + r, cy),
        (cx, cy + r),
        (cx - r, cy),
    ]
    grad = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
    draw_vertical_gradient(grad, (160, 240, 240), (80, 200, 200))
    # mask diamond onto grad
    mask = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
    pygame.gfxdraw.filled_polygon(mask, [(p[0]-cx+r+2, p[1]-cy+r+2) for p in pts], (255,255,255,255))
    grad.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - r - 2, cy - r - 2))
    # outline and shine
    pygame.gfxdraw.aapolygon(surf, pts, (40,140,140))
    shine = [(cx - r//2, cy - r//2), (cx + r//4, cy - r//2), (cx + r//2, cy)]
    pygame.draw.polygon(surf, (255,255,255,90), shine)


def draw_glossy_bomb(surf, tilex, tiley):
    cx = tilex * TILE_SIZE + TILE_SIZE // 2
    cy = tiley * TILE_SIZE + TILE_SIZE // 2
    r = TILE_SIZE // 3
    # glow
    glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for i in range(r*2, 0, -6):
        a = int(50 * (i / (r*2)))
        pygame.gfxdraw.filled_circle(glow, r*2, r*2, i, (220, 80, 10, a))
    surf.blit(glow, (cx - r*2, cy - r*2), special_flags=pygame.BLEND_ADD)
    # core
    pygame.gfxdraw.filled_circle(surf, cx, cy, r, (40, 40, 40))
    pygame.gfxdraw.filled_circle(surf, cx+int(r*0.2), cy-int(r*0.3), int(r*0.4), (180,60,40))
    pygame.gfxdraw.aacircle(surf, cx, cy, r, (0,0,0))


def draw_tile_bevel(surf, rect):
    # base
    pygame.draw.rect(surf, (240,240,240), rect, border_radius=6)
    # top highlight
    top = pygame.Rect(rect.x+2, rect.y+2, rect.w-4, rect.h//2)
    s = pygame.Surface((top.w, top.h), pygame.SRCALPHA)
    draw_vertical_gradient(s, (255,255,255,80), (255,255,255,0))
    surf.blit(s, (top.x, top.y))

def compute_path_and_target(sx, sy, dx, dy):
    path = []
    x, y = sx, sy
    bomb_hit = None
    while True:
        x += dx
        y += dy
        if not tile_in_bounds(x, y):
            x -= dx
            y -= dy
            break
        cell = grid[y][x]
        if cell == '#':
            x -= dx
            y -= dy
            break
        path.append((x, y))
        if cell == 'B':
            bomb_hit = (x, y)
            break
        if cell == 'S':
            break
    return path, (x, y), bomb_hit

def choose_direction_from_mouse(mx, my):
    px, py = player_pos
    vx = mx - px
    vy = my - py
    if vx == 0 and vy == 0:
        return None
    best = None
    best_dot = -999
    mag = math.hypot(vx, vy)
    vx /= mag
    vy /= mag
    for d in dirs8:
        dx, dy = d
        dd = math.hypot(dx, dy)
        ddx, ddy = dx / dd, dy / dd
        dot = vx * ddx + vy * ddy
        if dot > best_dot:
            best_dot = dot
            best = d
    return best

font = pygame.font.SysFont(None, 20)

running = True

# track mouse hover
mouse_hover = (-1, -1)

# small helper to spawn gem particles
def spawn_gem_particles(tilex, tiley):
    cx = tilex * TILE_SIZE + TILE_SIZE // 2
    cy = tiley * TILE_SIZE + TILE_SIZE // 2
    for i in range(12):
        ang = i * (2 * math.pi / 12) + random.random()
        vx = math.cos(ang) * (1 + (i % 3))
        vy = math.sin(ang) * (1 + (i % 3)) - 2
        particles.append(Particle((cx, cy), (vx, vy), (120, 220, 220), 40, 3))

def spawn_collect_particles(cx, cy, color=(120,220,220)):
    for _ in range(12):
        vx = (random.random() - 0.5) * 6
        vy = (random.random() - 0.5) * 6
        particles.append(Particle((cx, cy), (vx, vy), color, 40, 3))
# (mouse hover variable defined above)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_r:
                # restart
                grid = [list(row) for row in LEVEL]
                player_tile_x, player_tile_y = find_player()
                player_pos = [player_tile_x * TILE_SIZE + TILE_SIZE // 2, player_tile_y * TILE_SIZE + TILE_SIZE // 2]
                moving = False
                gems_collected = 0
                game_over = False
                game_won = False
            # keyboard directional controls (arrows, WASD, Q/E/Z/C for diagonals, keypad)
            if not moving and not game_over:
                key_dir = None
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    key_dir = (1, 0)
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    key_dir = (-1, 0)
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    key_dir = (0, -1)
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    key_dir = (0, 1)
                if event.key == pygame.K_q:
                    key_dir = (-1, -1)
                if event.key == pygame.K_e:
                    key_dir = (1, -1)
                if event.key == pygame.K_z:
                    key_dir = (-1, 1)
                if event.key == pygame.K_c:
                    key_dir = (1, 1)
                # keypad diagonals
                if event.key == pygame.K_KP1:
                    key_dir = (-1, 1)
                if event.key == pygame.K_KP3:
                    key_dir = (1, 1)
                if event.key == pygame.K_KP7:
                    key_dir = (-1, -1)
                if event.key == pygame.K_KP9:
                    key_dir = (1, -1)
                if key_dir is not None:
                    dx, dy = key_dir
                    path, target_tile, bomb = compute_path_and_target(player_tile_x, player_tile_y, dx, dy)
                    if path:
                        moving = True
                        move_dir = (dx, dy)
                        move_target = [target_tile[0] * TILE_SIZE + TILE_SIZE // 2, target_tile[1] * TILE_SIZE + TILE_SIZE // 2]
                        target_path = path
                        bomb_in_path = bomb
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not moving and not game_over:
            mx, my = event.pos
            d = choose_direction_from_mouse(mx, my)
            if d is not None:
                dx, dy = d
                path, target_tile, bomb = compute_path_and_target(player_tile_x, player_tile_y, dx, dy)
                if path:
                    moving = True
                    move_dir = (dx, dy)
                    move_target = [target_tile[0] * TILE_SIZE + TILE_SIZE // 2, target_tile[1] * TILE_SIZE + TILE_SIZE // 2]
                    target_path = path
                    bomb_in_path = bomb
    if moving and not game_over:
        px, py = player_pos
        tx, ty = move_target
        vx = tx - px
        vy = ty - py
        dist = math.hypot(vx, vy)
        if dist <= move_speed:
            player_pos[0], player_pos[1] = tx, ty
            player_tile_x = tx // TILE_SIZE
            player_tile_y = ty // TILE_SIZE
            moving = False
            if tile_in_bounds(player_tile_x, player_tile_y) and grid[player_tile_y][player_tile_x] == 'B':
                bx = player_tile_x * TILE_SIZE + TILE_SIZE // 2
                by = player_tile_y * TILE_SIZE + TILE_SIZE // 2
                spawn_collect_particles(bx, by, (220, 80, 10))
                game_over = True
        else:
            vx /= dist
            vy /= dist
            player_pos[0] += vx * move_speed
            player_pos[1] += vy * move_speed
            cx = int(player_pos[0]) // TILE_SIZE
            cy = int(player_pos[1]) // TILE_SIZE
            if tile_in_bounds(cx, cy) and grid[cy][cx] == 'G':
                # collect gem and spawn particles
                grid[cy][cx] = '.'
                gems_collected += 1
                px = cx * TILE_SIZE + TILE_SIZE // 2
                py = cy * TILE_SIZE + TILE_SIZE // 2
                spawn_collect_particles(px, py, (120, 220, 220))
                if gems_collected >= total_gems:
                    game_won = True
                    moving = False
            if tile_in_bounds(cx, cy) and grid[cy][cx] == 'B':
                # bomb explosion particles
                bx = cx * TILE_SIZE + TILE_SIZE // 2
                by = cy * TILE_SIZE + TILE_SIZE // 2
                spawn_collect_particles(bx, by, (220, 80, 10))
                game_over = True

    screen.fill((200, 200, 200))

    # update mouse hover tile
    mx, my = pygame.mouse.get_pos()
    hx, hy = mx // TILE_SIZE, my // TILE_SIZE
    if 0 <= hx < GRID_W and 0 <= hy < GRID_H:
        mouse_hover = (hx, hy)
    else:
        mouse_hover = (-1, -1)

    # compute path preview from hover direction
    preview_path = []
    preview_target = None
    if not moving and not game_over:
        md = choose_direction_from_mouse(mx, my)
        if md is not None:
            pdx, pdy = md
            ppath, ptile, _ = compute_path_and_target(player_tile_x, player_tile_y, pdx, pdy)
            preview_path = ppath
            preview_target = ptile

    for y in range(GRID_H):
        for x in range(GRID_W):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            cell = grid[y][x]
            if cell == '#':
                pygame.draw.rect(screen, (120, 120, 120), rect)
            else:
                pygame.draw.rect(screen, (230, 230, 230), rect)
            if cell == 'S':
                pygame.draw.rect(screen, (200, 200, 200), rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 3)
            if cell == 'B':
                cx = x * TILE_SIZE + TILE_SIZE // 2
                cy = y * TILE_SIZE + TILE_SIZE // 2
                # pulsing bomb
                t = pygame.time.get_ticks() * 0.006
                pulse = 1 + 0.08 * math.sin(t + x + y)
                r = int(TILE_SIZE // 3 * pulse)
                pygame.draw.circle(screen, (30, 30, 30), (cx, cy), r)
                pygame.draw.circle(screen, (0, 0, 0), (cx, cy), max(2, r-6))
            if cell == 'G':
                # animated gem pulse
                cx = x * TILE_SIZE + TILE_SIZE // 2
                cy = y * TILE_SIZE + TILE_SIZE // 2
                t = pygame.time.get_ticks() * 0.008
                s = 1.0 + 0.12 * math.sin(t + x * 0.4 + y * 0.6)
                r = int((TILE_SIZE // 4) * s)
                pts = [
                    (cx, cy - r),
                    (cx + r, cy),
                    (cx, cy + r),
                    (cx - r, cy),
                ]
                pygame.draw.polygon(screen, (120, 220, 220), pts)
                pygame.draw.polygon(screen, (80, 180, 180), pts, 2)
            # preview overlay
            if (x, y) in preview_path:
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                s.fill((255, 255, 120, 60))
                screen.blit(s, (x * TILE_SIZE, y * TILE_SIZE))
            if preview_target and (x, y) == preview_target:
                # target marker
                tt = pygame.Rect(x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2)
                pygame.draw.rect(screen, (255, 220, 120), tt, 3, border_radius=6)
            # highlight hovered tile when not moving
            if (x, y) == mouse_hover and not moving:
                pygame.draw.rect(screen, (255, 255, 200), rect, 3)
            pygame.draw.rect(screen, (150, 150, 150), rect, 1)

    # update and draw particles (behind player)
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    # trailing particles while moving
    if moving and not game_over:
        if random.random() < 0.35:
            px = player_pos[0] + (random.random() - 0.5) * 6
            py = player_pos[1] + (random.random() - 0.5) * 6
            particles.append(Particle((px, py), ((random.random()-0.5)*0.6, (random.random()-0.5)*0.6), (50,200,100), 18, 2))

    pygame.draw.circle(screen, (0, 180, 0), (int(player_pos[0]), int(player_pos[1])), TILE_SIZE // 3)

    hud = font.render(f"Gems: {gems_collected}/{total_gems}", True, (0, 0, 0))
    screen.blit(hud, (6, HEIGHT - 24))

    if game_over:
        over = font.render("Game Over - You hit a bomb. Press R to restart.", True, (200, 0, 0))
        screen.blit(over, (6, 6))
    if game_won:
        win = font.render("You collected all gems! Press R to restart.", True, (0, 150, 0))
        screen.blit(win, (6, 6))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
