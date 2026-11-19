import json
import random
import numpy as np


class PaintShopEnv:
    
    COLOR_NAMES = {
        1: "Siyah",
        2: "Gri",
        3: "Beyaz"
    }

    def __init__(self, black_order, grey_order, white_order):
        self.targets = [black_order, grey_order, white_order]
        self.reset()

    def reset(self):
        self.current_color = 0  
        self.left = self.targets.copy()
        self.painted_cars = 0
        self.color_changes = 0
        return self.get_state()

    def get_state(self):
        return (
            self.current_color,
            self.left[0],
            self.left[1],
            self.left[2]
        )

    def available_actions(self, state):
        _, left_black, left_grey, left_white = state
        remaining = [left_black, left_grey, left_white]
        return [action for action in range(3) if remaining[action] > 0]

    def step(self, action):
        if action not in self.available_actions(self.get_state()):
            raise ValueError("Seçilen renkten stok kalmamış.")

        target_color = action + 1

        if self.current_color == 0:
            reward = 1
        elif self.current_color == target_color:
            reward = 1
        else:
            reward = -100 

            self.color_changes += 1
        
        self.left[action] -= 1
        self.painted_cars += 1
        self.current_color = target_color

        done = all(quantity == 0 for quantity in self.left)
        return self.get_state(), reward, done



BLACK_ORDER = 8_000
GREY_ORDER = 4_000
WHITE_ORDER = 2_000

TOTAL_CARS = BLACK_ORDER + GREY_ORDER + WHITE_ORDER

random.seed(42)
np.random.seed(42)

env = PaintShopEnv(BLACK_ORDER, GREY_ORDER, WHITE_ORDER)


def encode_state(state):
    """
    Durumu kayıpsız kodlar:
    (son renk, kalan siyah, kalan gri, kalan beyaz)
    """
    current_color, left_black, left_grey, left_white = state

    code = current_color
    code = code * (BLACK_ORDER + 1) + left_black
    code = code * (GREY_ORDER + 1) + left_grey
    code = code * (WHITE_ORDER + 1) + left_white

    return code


def decode_state(code):
    """Kaydedilen sayısal anahtarı tekrar duruma çevirir."""
    left_white = code % (WHITE_ORDER + 1)
    code //= WHITE_ORDER + 1

    left_grey = code % (GREY_ORDER + 1)
    code //= GREY_ORDER + 1

    left_black = code % (BLACK_ORDER + 1)
    code //= BLACK_ORDER + 1

    current_color = code

    return current_color, left_black, left_grey, left_white


q_table = {}


def get_q_values(state):
    state_key = encode_state(state)

    if state_key not in q_table:
        q_table[state_key] = np.zeros(3, dtype=np.float32)

    return q_table[state_key]



ALPHA = 0.1
GAMMA = 1.0

EPISODES = 300
EPSILON = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.98


def choose_action(state, valid_actions, epsilon):
    
    if random.random() < epsilon:
        return random.choice(valid_actions)

    q_values = get_q_values(state)
    best_value = max(q_values[action] for action in valid_actions)

    best_actions = [
        action for action in valid_actions
        if np.isclose(q_values[action], best_value)
    ]

    current_color = state[0]
    current_action = current_color - 1

    if current_action in best_actions:
        return current_action

    return min(best_actions)


print(f"Eğitim başladı. Sipariş toplamı: {TOTAL_CARS:,} araç.")

recent_rewards = []

for episode in range(1, EPISODES + 1):
    state = env.reset()
    done = False
    episode_reward = 0

    while not done:
        valid_actions = env.available_actions(state)
        action = choose_action(state, valid_actions, EPSILON)

        next_state, reward, done = env.step(action)
        episode_reward += reward

        old_q = get_q_values(state)[action]

        if done:
            target_q = reward
        else:
            next_actions = env.available_actions(next_state)
            next_q_values = get_q_values(next_state)

            target_q = reward + GAMMA * max(
                next_q_values[next_action]
                for next_action in next_actions
            )

        get_q_values(state)[action] = old_q + ALPHA * (
            target_q - old_q
        )

        state = next_state

    EPSILON = max(EPSILON_MIN, EPSILON * EPSILON_DECAY)
    recent_rewards.append(episode_reward)

    if len(recent_rewards) > 50:
        recent_rewards.pop(0)

    if episode % 10 == 0:
        print(
            f"Bölüm {episode}/{EPISODES} | "
            f"Son bölümlerin ortalama ödülü: "
            f"{np.mean(recent_rewards):,.2f} | "
            f"Epsilon: {EPSILON:.3f} | "
            f"Q durumu: {len(q_table):,}"
        )

print("Eğitim tamamlandı.")

q_table_json = {}

for state_key, q_values in q_table.items():
    state = decode_state(state_key)
    state_text = ",".join(map(str, state))
    q_table_json[state_text] = q_values.tolist()

with open("QTable.json", "w", encoding="utf-8") as file:
    json.dump(q_table_json, file, ensure_ascii=False)

print(f"QTable.json kaydedildi. Durum sayısı: {len(q_table_json):,}")


test_env = PaintShopEnv(BLACK_ORDER, GREY_ORDER, WHITE_ORDER)
state = test_env.reset()
done = False
total_reward = 0

print("\nQ-LEARNING TESTİ")
print("-" * 90)

while not done:
    previous_color = state[0]
    valid_actions = test_env.available_actions(state)

   
    action = choose_action(state, valid_actions, epsilon=0.0)

    state, reward, done = test_env.step(action)
    total_reward += reward

    selected_color = action + 1
    color_changed = previous_color != selected_color

    if (
        color_changed
        or test_env.painted_cars % 1000 == 0
        or done
    ):
        previous_name = (
            PaintShopEnv.COLOR_NAMES.get(previous_color, "Başlangıç")
        )

        print(
            f"Araç {test_env.painted_cars:>6,} | "
            f"{previous_name:>9} -> "
            f"{PaintShopEnv.COLOR_NAMES[selected_color]:<6} | "
            f"Kalan stok: "
            f"Siyah={test_env.left[0]:,}, "
            f"Gri={test_env.left[1]:,}, "
            f"Beyaz={test_env.left[2]:,} | "
            f"Ödül: {reward}"
        )

print("-" * 90)
print(f"Boyanan araç sayısı: {test_env.painted_cars:,}")
print(f"Renk değişim sayısı: {test_env.color_changes}")
print(f"Test toplam ödülü: {total_reward:,}")