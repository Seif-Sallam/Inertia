# Inertia Game Documentation

## Overview
Inertia is a grid-based puzzle game where the player slides in straight lines, collecting gems and avoiding bombs. The game features procedural level generation, smooth movement, particle effects, and a win/lose system. This documentation covers the entire game flow, logic, and UI, to assist porting to HTML + JavaScript for hosting on GitHub Pages.

---

## Game Flow

### 1. Initialization
- The game initializes the window, grid size, and tile size.
- Procedural generation creates a new level with walls, gems, bombs, and a player start position.

### 2. Level Generation
- **Walls**: Placed randomly, with density increasing by level.
- **Bombs**: Placed randomly, with density increasing by level.
- **Gems**: Placed randomly, with density increasing by level. At least one gem is guaranteed.
- **Player**: Starts at a safe tile, usually near the center.

### 3. Player Controls
- **Keyboard**: Arrow keys, WASD, Q/E/Z/C, and numpad diagonals move the player in 8 directions.
- **Mouse**: Click in a direction to move.
- The player slides in the chosen direction until hitting a wall, bomb, or special tile.

### 4. Movement & Pathfinding
- The player moves in a straight line until blocked.
- If a gem is encountered, it is collected.
- If a bomb is encountered, the game ends with an explosion effect.
- If all gems are collected, the level is won and auto-advances after a short timer.

### 5. Game States
- **Active**: Player can move and collect gems.
- **Game Over**: Triggered by hitting a bomb. Displays a message and allows restart.
- **Win**: Triggered by collecting all gems. Displays a message and auto-advances to the next level.

### 6. UI & Visuals
- **Grid**: Tiles are rendered with bevels, gradients, and highlights.
- **Player**: Rendered as a glossy circle.
- **Gems/Bombs**: Rendered with custom glossy effects and particles.
- **Particles**: Used for gem collection, movement trails, and explosions.
- **HUD**: Displays gems collected, total gems, and current level.
- **Preview**: Shows the path the player will take before moving.

### 7. Level Progression
- Levels increase in difficulty by adding more walls, bombs, and gems.
- The player can restart the current level or advance to the next.

---

## Porting Notes (HTML + JavaScript)
- **Grid Logic**: Use 2D arrays for grid state.
- **Rendering**: Use Canvas API for drawing tiles, player, gems, bombs, and particles.
- **Input**: Map keyboard and mouse events to movement logic.
- **Procedural Generation**: Port the level generation logic, including random walks and density scaling.
- **Particles/Effects**: Use requestAnimationFrame for smooth animations.
- **Game Loop**: Implement a main loop for updating state and rendering.
- **Responsive UI**: Adapt grid and tile size for different screen sizes.

---

## Main Classes & Functions
- **Level Generation**: Generates grid, places walls, gems, bombs, and player.
- **Player Movement**: Handles input, computes path, updates position.
- **Particles/Explosion**: Manages visual effects for polish.
- **Rendering**: Draws all game elements and HUD.

---

## Win/Lose Conditions
- **Win**: Collect all gems.
- **Lose**: Hit a bomb.
- **Restart**: Press R to restart the level.
- **Advance**: Press N or auto-advance after win timer.

---

## UI Elements
- **Grid**: Main play area.
- **Player**: Green glossy circle.
- **Gems**: Blue glossy diamonds.
- **Bombs**: Red glossy circles.
- **HUD**: Gem count, level number.
- **Messages**: Game over, win, restart instructions.

---

## Suggestions for HTML/JS Port
- Use modular code: separate logic, rendering, and input.
- Use ES6 classes for game entities.
- Store game state in objects.
- Use CSS for layout and responsive design.
- Optimize for performance and smooth animations.

---

## License & Attribution
- Original Python code by author.
- Porting and hosting allowed for educational and non-commercial use.

---

For further details, see the Python source code and comments. This documentation is designed to guide a full-featured port to HTML + JavaScript for web hosting.
