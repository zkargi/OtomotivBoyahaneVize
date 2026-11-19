import json
import random
import numpy as np


class PaintShopEnv:
    def __init__(
        self,
        target_black: int,
        target_grey: int,
        target_white: int,
        batch_size: int = 100,
    ):
        assert batch_size > 0, "batch_size pozitif olmalı."
        assert min(target_black, target_grey, target_white) >= 0, "Sipariş negatif olamaz."

        self.batch_size = batch_size
        # Stoklar araç sayısı olarak tutulur; her adımda min(batch_size, kalan) araç boyanır.
        self.init_black = target_black
        self.init_grey = target_grey
        self.init_white = target_white
        self.total_vehicles = target_black + target_grey + target_white
        self.last_painted = 0
        self.reset()

    def reset(self):
        self.current_color = 0  # 0: henüz boyama yapılmadı
        self.left_black = self.init_black
        self.left_grey = self.init_grey
        self.left_white = self.init_white
        return self._get_state()

    def _get_state(self):
        return (self.current_color, self.left_black, self.left_grey, self.left_white)

    def valid_actions(self):
        actions = []
        if self.left_black > 0:
            actions.append(0)
        if self.left_grey > 0:
            actions.append(1)
        if self.left_white > 0:
            actions.append(2)
        return actions

    def step(self, action: int):
        target_color = action + 1  # 1: Siyah, 2: Gri, 3: Beyaz

        if (
            (target_color == 1 and self.left_black == 0)
            or (target_color == 2 and self.left_grey == 0)
            or (target_color == 3 and self.left_white == 0)
        ):
            return self._get_state(), -100, False

        if self.current_color == 0 or self.current_color == target_color:
            reward = 1
        else:
            reward = -100

        self.current_color = target_color
        if target_color == 1:
            self.last_painted = min(self.batch_size, self.left_black)
            self.left_black -= self.last_painted
        elif target_color == 2:
            self.last_painted = min(self.batch_size, self.left_grey)
            self.left_grey -= self.last_painted
        elif target_color == 3:
            self.last_painted = min(self.batch_size, self.left_white)
            self.left_white -= self.last_painted

        done = self.left_black == 0 and self.left_grey == 0 and self.left_white == 0
        return self._get_state(), reward, done


q_table = {}

alpha = 0.1
gamma = 0.9
epsilon = 0.9
epsilon_min = 0.01
epsilon_decay = 0.999
episodes = 20000


def get_q_values(state):
    if state not in q_table:
        q_table[state] = np.zeros(3, dtype=np.float64)
    return q_table[state]


def best_valid_action(state, valid_actions):
    q_vals = get_q_values(state)
    current_action = state[0] - 1 if state[0] in (1, 2, 3) else -1
    return max(
        valid_actions,
        key=lambda a: (q_vals[a], 1 if a == current_action else 0),
    )


env = PaintShopEnv(
    target_black=7050,
    target_grey=4000,
    target_white=1000,
    batch_size=100,
)
print("Eğitim başlıyor. Lütfen bekleyin...")

for ep in range(episodes):
    state = env.reset()
    done = False
    current_eps = 0.0 if ep >= int(episodes * 0.85) else epsilon

    while not done:
        valid = env.valid_actions()
        if random.uniform(0, 1) < current_eps:
            action = random.choice(valid)
        else:
            action = best_valid_action(state, valid)

        next_state, reward, done = env.step(action)

        old_q = get_q_values(state)[action]
        if done:
            next_max = 0.0
        else:
            next_valid = env.valid_actions()
            next_max = max(get_q_values(next_state)[a] for a in next_valid)

        q_table[state][action] = old_q + alpha * (reward + gamma * next_max - old_q)
        state = next_state

    epsilon = max(epsilon_min, epsilon * epsilon_decay)

print("Eğitim tamamlandı! JSON dosyası oluşturuluyor...\n")

q_table_str_keys = {
    f"{s[0]},{s[1]},{s[2]},{s[3]}": vals.tolist() for s, vals in q_table.items()
}

with open("QTable.json", "w", encoding="utf-8") as outfile:
    json.dump(q_table_str_keys, outfile)

print("QTable.json başarıyla kaydedildi\n")

# --- TERMİNAL ÇIKTISI ---
print("-" * 60)
print("OPTIMAL POLICY...")
print("-" * 60)

state = env.reset()
done = False
total_reward = 0
step_count = 1
painted_vehicles = 0
color_names = {1: "Siyah", 2: "Gri", 3: "Beyaz"}

while not done:
    valid = env.valid_actions()
    action = best_valid_action(state, valid)
    next_state, reward, done = env.step(action)

    target_color = action + 1
    color_str = color_names[target_color]
    painted_vehicles += env.last_painted

    print(
        f"Adım {step_count:03d} | Seçilen: {color_str:5} (+{env.last_painted:03d} araç) | "
        f"Kalan Araç -> Siyah: {next_state[1]:04d}, Gri: {next_state[2]:04d}, Beyaz: {next_state[3]:04d} | "
        f"Ceza/Ödül: {reward}"
    )

    total_reward += reward
    state = next_state
    step_count += 1

print("-" * 60)
print(f"Boyanan Araç Sayısı: {painted_vehicles}")
print(f"Toplam Kazanılan Puan : {total_reward}")
print("-" * 60)
