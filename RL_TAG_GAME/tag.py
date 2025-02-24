import pygame
import random
import numpy as np
import sys
from collections import deque

# ----------------------------------------
# GLOBAL PARAMETERS
# ----------------------------------------
GRID_SIZE = 5         # 5x5 grid
CELL_SIZE = 80        # Size of each cell in the main grid
SIDE_PANEL_WIDTH = 220
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE + SIDE_PANEL_WIDTH
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE

FPS = 5               # Initial frames per second (speed of visualization)
NUM_EPISODES = 3000   # Number of training episodes
MAX_STEPS = 30        # Max steps per episode before termination

ALPHA = 0.1           # Learning rate
GAMMA = 0.9           # Discount factor
EPSILON_START = 1.0   # Starting epsilon for ε-greedy
EPSILON_END = 0.05    # Minimum epsilon
EPSILON_DECAY = 0.995 # Factor to decay epsilon each episode

# Actions: 0=Up, 1=Right, 2=Down, 3=Left, 4=Stay
ACTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
ACTION_NAMES = ["Up", "Right", "Down", "Left", "Stay"]

# Colors
WHITE  = (255, 255, 255)
BLACK  = (  0,   0,   0)
RED    = (255,   0,   0)
BLUE   = (  0,   0, 255)
GREEN  = (  0, 255,   0)
GRAY   = ( 50,  50,  50)
LIGHT_GRAY = (200, 200, 200)

# ----------------------------------------
# Q-Tables
# Q-Table shape: (GRID_SIZE, GRID_SIZE, GRID_SIZE, GRID_SIZE, 5)
# Index: [Tx, Ty, Rx, Ry, action] -> Q-value
# ----------------------------------------
q_table_tagger = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE, GRID_SIZE, len(ACTIONS)))
q_table_runner = np.zeros((GRID_SIZE, GRID_SIZE, GRID_SIZE, GRID_SIZE, len(ACTIONS)))

# To track rewards over episodes
runner_reward_history = deque(maxlen=100)  # store last 100 episode rewards
tagger_reward_history = deque(maxlen=100)  # store last 100 episode rewards

def get_state(tagger_pos, runner_pos):
    """Return a tuple that can be used to index Q-tables."""
    return (tagger_pos[0], tagger_pos[1], runner_pos[0], runner_pos[1])

def choose_action(q_table, state, epsilon):
    """ε-greedy action selection."""
    if random.random() < epsilon:
        return random.randint(0, len(ACTIONS)-1)
    else:
        q_values = q_table[state[0], state[1], state[2], state[3], :]
        return np.argmax(q_values)

def step_agent(pos, action):
    """Given an agent position and an action, return the new position on the grid."""
    dx, dy = ACTIONS[action]
    new_x = max(0, min(GRID_SIZE - 1, pos[0] + dx))
    new_y = max(0, min(GRID_SIZE - 1, pos[1] + dy))
    return (new_x, new_y)

def run_episode(epsilon):
    """
    Run one training episode:
     1. Initialize environment
     2. For each step:
        - Runner chooses action, environment updates runner, reward for runner
        - Tagger chooses action, environment updates tagger, reward for tagger
     3. Update Q-tables
    Return total rewards (runner, tagger).
    """
    # Random initial positions
    runner_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    tagger_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    while runner_pos == tagger_pos:
        # ensure they don't start in the same cell
        tagger_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

    runner_total_reward = 0
    tagger_total_reward = 0

    for _ in range(MAX_STEPS):
        # Step 1: Runner acts
        state_before_runner = get_state(tagger_pos, runner_pos)
        runner_action = choose_action(q_table_runner, state_before_runner, epsilon)
        new_runner_pos = step_agent(runner_pos, runner_action)

        # Calculate immediate reward for runner
        # The runner receives +1 if it is not caught yet, otherwise -10 if caught
        if new_runner_pos == tagger_pos:
            # Runner is caught
            runner_reward = -10
            done = True
        else:
            runner_reward = +1
            done = False

        # Step 2: Tagger acts (if not done)
        state_before_tagger = get_state(tagger_pos, runner_pos)
        if not done:
            tagger_action = choose_action(q_table_tagger, state_before_tagger, epsilon)
            new_tagger_pos = step_agent(tagger_pos, tagger_action)

            # Reward for tagger
            if new_tagger_pos == new_runner_pos:
                # Caught the runner
                tagger_reward = +10
                done = True
            else:
                tagger_reward = -1
        else:
            # Episode ends, no move for tagger if runner got caught on runner's turn
            new_tagger_pos = tagger_pos
            tagger_action = 4  # "Stay"
            tagger_reward = 0  # or -1, but typically 0

        # Next state
        new_state = get_state(new_tagger_pos, new_runner_pos)

        # Q-Update for runner
        old_q_runner = q_table_runner[state_before_runner + (runner_action,)]
        best_future_q_runner = np.max(q_table_runner[new_state])
        q_table_runner[state_before_runner + (runner_action,)] = old_q_runner + ALPHA * (
            runner_reward + GAMMA * best_future_q_runner - old_q_runner
        )

        # Q-Update for tagger
        old_q_tagger = q_table_tagger[state_before_tagger + (tagger_action,)]
        best_future_q_tagger = np.max(q_table_tagger[new_state])
        q_table_tagger[state_before_tagger + (tagger_action,)] = old_q_tagger + ALPHA * (
            tagger_reward + GAMMA * best_future_q_tagger - old_q_tagger
        )

        # Update positions
        runner_pos = new_runner_pos
        tagger_pos = new_tagger_pos

        # Accumulate rewards
        runner_total_reward += runner_reward
        tagger_total_reward += tagger_reward

        if done:
            break

    return runner_total_reward, tagger_total_reward

def draw_grid(screen):
    """Draw the 5x5 grid cells."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            # Fill cell with a darker background color for aesthetics
            if (x + y) % 2 == 0:
                pygame.draw.rect(screen, (60, 60, 60), rect)
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect)
            pygame.draw.rect(screen, BLACK, rect, 1)

def draw_side_panel(screen, font, episode_count, epsilon, step, runner_avg_reward, tagger_avg_reward):
    """Draw the side panel with stats."""
    panel_x = GRID_SIZE * CELL_SIZE  # left boundary of the side panel
    panel_rect = pygame.Rect(panel_x, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)

    # Fill side panel background
    pygame.draw.rect(screen, (30, 30, 30), panel_rect)

    # Prepare text
    title_text = font.render("RL Tag Game", True, GREEN)
    screen.blit(title_text, (panel_x + 20, 20))

    episode_text = font.render(f"Episode: {episode_count} / {NUM_EPISODES}", True, WHITE)
    screen.blit(episode_text, (panel_x + 20, 60))

    step_text = font.render(f"Step: {step}", True, WHITE)
    screen.blit(step_text, (panel_x + 20, 90))

    epsilon_text = font.render(f"Epsilon: {epsilon:.2f}", True, WHITE)
    screen.blit(epsilon_text, (panel_x + 20, 120))

    runner_reward_text = font.render(f"Runner Avg R: {runner_avg_reward:.2f}", True, WHITE)
    screen.blit(runner_reward_text, (panel_x + 20, 160))

    tagger_reward_text = font.render(f"Tagger Avg R: {tagger_avg_reward:.2f}", True, WHITE)
    screen.blit(tagger_reward_text, (panel_x + 20, 190))

    speed_text = font.render(f"FPS: {FPS}", True, WHITE)
    screen.blit(speed_text, (panel_x + 20, 230))

def draw_agents(screen, runner_pos, tagger_pos, font):
    """Draw the runner and tagger circles plus their labels."""
    # Runner
    runner_x = runner_pos[0] * CELL_SIZE + CELL_SIZE // 2
    runner_y = runner_pos[1] * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, RED, (runner_x, runner_y), 15)
    runner_label = font.render("Runner", True, WHITE)
    screen.blit(runner_label, (runner_x - 25, runner_y - 35))

    # Tagger
    tagger_x = tagger_pos[0] * CELL_SIZE + CELL_SIZE // 2
    tagger_y = tagger_pos[1] * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, BLUE, (tagger_x, tagger_y), 15)
    tagger_label = font.render("Tagger", True, WHITE)
    screen.blit(tagger_label, (tagger_x - 25, tagger_y - 35))

def visualize_episode(screen, clock, episode_count, epsilon):
    """
    Visualize one episode with the current Q-tables.
    This does not update Q-tables, just visualizes a 'play' to see how the agents behave.
    """
    # We pick random start positions
    runner_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    tagger_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
    while runner_pos == tagger_pos:
        tagger_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))

    step_count = 0
    done = False

    # For side panel stats (no real rewards here, but we can show rolling average)
    runner_avg_reward = np.mean(runner_reward_history) if len(runner_reward_history) > 0 else 0.0
    tagger_avg_reward = np.mean(tagger_reward_history) if len(tagger_reward_history) > 0 else 0.0

    font = pygame.font.SysFont(None, 24)

    while step_count < MAX_STEPS and not done:
        clock.tick(FPS)
        step_count += 1

        # 1) Draw environment background
        screen.fill(BLACK)
        draw_grid(screen)

        # 2) Draw side panel
        draw_side_panel(screen, font, episode_count, epsilon, step_count, runner_avg_reward, tagger_avg_reward)

        # 3) Draw agents
        draw_agents(screen, runner_pos, tagger_pos, font)

        pygame.display.flip()

        # Runner picks action (greedy/epsilon)
        state_before_runner = get_state(tagger_pos, runner_pos)
        runner_action = choose_action(q_table_runner, state_before_runner, epsilon)
        new_runner_pos = step_agent(runner_pos, runner_action)

        if new_runner_pos == tagger_pos:
            # Runner caught instantly
            done = True
            continue

        # Tagger picks action
        state_before_tagger = get_state(tagger_pos, runner_pos)
        tagger_action = choose_action(q_table_tagger, state_before_tagger, epsilon)
        new_tagger_pos = step_agent(tagger_pos, tagger_action)

        runner_pos = new_runner_pos
        tagger_pos = new_tagger_pos

        if runner_pos == tagger_pos:
            done = True

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RL Tag Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    running = True
    episode_count = 0
    epsilon = EPSILON_START

    while running:
        # 1) Run training episodes in batches
        BATCH_SIZE = 50  
        for _ in range(BATCH_SIZE):
            runner_r, tagger_r = run_episode(epsilon)
            runner_reward_history.append(runner_r)
            tagger_reward_history.append(tagger_r)
            # Decay epsilon
            epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)
            episode_count += 1
            if episode_count >= NUM_EPISODES:
                break
        
        # 2) After batch training, visualize one episode
        visualize_episode(screen, clock, episode_count, epsilon)

        # 3) Handle events (exit or speed control)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    # Increase speed
                    global FPS
                    FPS = min(60, FPS + 1)
                elif event.key == pygame.K_DOWN:
                    # Decrease speed
                    FPS = max(1, FPS - 1)

        if episode_count >= NUM_EPISODES:
            # Training is done; you can keep visualizing or exit automatically.
            # We'll just keep it running so you can watch final strategies.
            pass

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
