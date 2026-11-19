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
        self.batch_size = max(1, batch_size)
        self.init_black = max(1, target_black // self.batch_size)
        self.init_grey = max(1, target_grey // self.batch_size)
        self.init_white = max(1, target_white // self.batch_size)
        self.total_vehicles = (
            self.init_black + self.init_grey + self.init_white
        ) * self.batch_size
        self.reset()

    def reset(self):
        self.current_color = 0  #
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
            self.left_black -= 1
        elif target_color == 2:
            self.left_grey -= 1
        elif target_color == 3:
            self.left_white -= 1

        done = self.left_black == 0 and self.left_grey == 0 and self.left_white == 0
        return self._get_state(), reward, done


q_table = {}

alpha = 0.15
gamma = 0.95
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
    target_black=7000,
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
    painted_vehicles += env.batch_size

    print(
        f"Adım {step_count:03d} | Seçilen: {color_str:5} (+{env.batch_size} araç) | "
        f"Kalan Parti -> Siyah: {next_state[1]:02d}, Gri: {next_state[2]:02d}, Beyaz: {next_state[3]:02d} | "
        f"Ceza/Ödül: {reward}"
    )

    total_reward += reward
    state = next_state
    step_count += 1

print("-" * 60)
print(f"Boyanan Araç Sayısı: {painted_vehicles}")
print(f"Toplam Kazanılan Puan : {total_reward}")
print("-" * 60)