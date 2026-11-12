import numpy as np
import random
import json

class PaintShopEnv:
    def __init__(self, target_black, target_grey, target_white):
        self.target_black = target_black
        self.target_grey = target_grey
        self.target_white = target_white
        self.reset()
        
    def reset(self):
        self.current_color = 0 
        self.left_black = self.target_black
        self.left_grey = self.target_grey
        self.left_white = self.target_white
        return self._get_state()
        
    def _get_state(self):
        return (self.current_color, self.left_black, self.left_grey, self.left_white)
        
    def step(self, action):
        # 1: Siyah, 2: Gri, 3: Beyaz
        target_color = action + 1 
        
        if (target_color == 1 and self.left_black == 0) or \
           (target_color == 2 and self.left_grey == 0) or \
           (target_color == 3 and self.left_white == 0):
            reward = -100
            return self._get_state(), reward, False 

        # Ödül - Ceza 
        if self.current_color == 0:
            reward = 1  
        elif self.current_color == target_color:
            reward = 1  
        else:
            if self.current_color == 1 and target_color == 3:
                reward = -100 
            elif self.current_color == 3 and target_color == 1:
                reward = -75
            else:
                reward = -50 

        
        self.current_color = target_color
        
        if target_color == 1:
            self.left_black -= 1
        elif target_color == 2:
            self.left_grey -= 1
        elif target_color == 3:
            self.left_white -= 1

        
        done = (self.left_black == 0 and self.left_grey == 0 and self.left_white == 0)

        return self._get_state(), reward, done


env = PaintShopEnv(target_black=23, target_grey=14, target_white=9)
q_table = {}

alpha = 0.1      
gamma = 0.9      
epsilon = 0.9    
episodes = 20000 

def get_q_values(state):
    if state not in q_table:
        q_table[state] = np.zeros(3) 
    return q_table[state]

print("Eğitim başlıyor. Lütfen bekleyin...")


for i in range(episodes):
    state = env.reset()
    done = False
    
    while not done:
        if random.uniform(0, 1) < epsilon:
            action = random.randint(0, 2) 
        else:
            action = np.argmax(get_q_values(state)) 
            
        next_state, reward, done = env.step(action)
        
        old_q_value = get_q_values(state)[action]
        next_max = np.max(get_q_values(next_state))
        
        new_q_value = old_q_value + alpha * (reward + gamma * next_max - old_q_value)
        q_table[state][action] = new_q_value
        
        state = next_state
        
    epsilon = max(0.1, epsilon * 0.999) 

print("Eğitim tamamlandı! JSON dosyası oluşturuluyor...\n")


q_table_str_keys = {}
for state, q_values in q_table.items():
    state_str = f"{state[0]},{state[1]},{state[2]},{state[3]}" 
    q_table_str_keys[state_str] = q_values.tolist()

with open("QTable.json", "w") as outfile:
    json.dump(q_table_str_keys, outfile)

print("QTable.json başarıyla kaydedildi\n")

# --- TERMİNAL ÇIKTISI  ---
print("-" * 60)
print("EĞİTİLMİŞ YAPAY ZEKA TEST EDİLİYOR (OPTIMAL POLICY)...")
print("-" * 60)

state = env.reset()
done = False
total_reward = 0
step_count = 1
color_names = {1: "Siyah", 2: "Gri", 3: "Beyaz"}

while not done:
    
    action = np.argmax(get_q_values(state))
    next_state, reward, done = env.step(action)
    
    target_color = action + 1
    color_str = color_names[target_color]
    
    # Terminal- anlık durum
    print(f"Adım {step_count:02d} | Seçilen: {color_str:5} | Kalan Sipariş Sayısı -> Siyah: {next_state[1]:02d}, Gri: {next_state[2]:02d}, Beyaz: {next_state[3]:02d} | Ceza/Ödül: {reward}")
    
    total_reward += reward
    state = next_state
    step_count += 1

print("-" * 60)
print(f"Boyanan Araç Sayısı: {step_count - 1}")
print(f"Toplam Kazanılan Puan : {total_reward}")
print("-" * 60)