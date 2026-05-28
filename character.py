import random
import json
import item

class professor:
    def __init__(self, prof: dict):
        self.name = prof['name']
        self.field = prof['field']
        self.subjects = prof['subjects']
        self.affinity = random.randint(20, 30)  # 隨機生成親密度 (20-30) 滿級 100
        self.position = (0, 0)  # 教授的初始位置，進入地圖後會被更新

class boss:
    def __init__(self, boss: dict):
        self.name = boss['name']
        self.field = boss['field']
        self.health = boss['health']
        self.position = (0, 0)  # 怨靈的初始位置，進入地圖後會被更新

class player:
    def __init__(self, name, sex):
        self.name = name
        self.sex = sex
        self.map = None
        self.position = (0, 0)
        self.health = 100
        self.analysis = 0
        self.algebra = 0
        self.geometry = 0

    def move(self, direction):
        """處理玩家的移動請求"""
        r, c = self.position
        # 定義移動方向的座標變化
        moves = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}

        if direction in moves:
            dr, dc = moves[direction]
            next_pos = (r + dr, c + dc)

            # 判斷目標格子是否存在於「當前格子的可通行列表」中
            if next_pos in self.map.connections[(r, c)]:
                self.position = next_pos
            else:
                print("撞到牆壁或邊界了！無法往該方向移動。")
        else:
            print("無效的輸入。請輸入 w/a/s/d。")

    def get_item(self):
        pass

    def talk(self, prof: professor):
        print(f"{prof.name} 教授好！")
        if prof.affinity < 30:
            print(f"{prof.name}：同學你是新來的吧？叫什麼名字？")
            print(f"{self.name}：我叫 {self.name}。")
            print("你向教授自我介紹，親密度增加了！")
            prof.affinity += 10  # 增加親密度
        else:
            print(f"{prof.name}：{self.name}，找我有什麼事嗎？")
            print(f"{self.name}：我想請教一些關於 {random.choice(prof.subjects)} 的問題。")
            print("教授很樂意幫助你，親密度增加了！")
            prof.affinity += random.random() * 10  # 增加親密度
            upgrade = random.random() * prof.affinity/10  # 根據親密度增加能力值
            if prof.field == "Algebra":
                self.algebra += upgrade  # 根據親密度增加代數能力
            elif prof.field == "Geometry":
                self.geometry += upgrade  # 根據親密度增加幾何能力
            elif prof.field == "Analysis":
                self.analysis += upgrade  # 根據親密度增加分析能力
        print("目前的能力值如下")
        print(f"代數能力：{self.algebra:.2f}，幾何能力：{self.geometry:.2f}，分析能力：{self.analysis:.2f}。")

    def battle(self, enemy: boss):
        command = input("A 代數之力 G 幾何之力 N 分析之力 H 回血 R 逃跑\n請輸入指令：")

        if command == 'A':
            if enemy.field == "Algebra":
                damage = self.algebra * random.random() * 20  # 對弱點造成更多傷害
            else:
                damage = self.algebra * random.random() * 10
            enemy.health -= damage
            print(f"你使用了代數之力，對 {enemy.name} 造成了 {damage:.2f} 點傷害！")
        elif command == 'G':
            if enemy.field == "Geometry":
                damage = self.geometry * random.random() * 20  # 對弱點造成更多傷害
            else:
                damage = self.geometry * random.random() * 10
            enemy.health -= damage
            print(f"你使用了幾何之力，對 {enemy.name} 造成了 {damage:.2f} 點傷害！")
        elif command == 'N':
            if enemy.field == "Analysis":
                damage = self.analysis * random.random() * 20  # 對弱點造成更多傷害
            else:
                damage = self.analysis * random.random() * 10
            enemy.health -= damage
            print(f"你使用了分析之力，對 {enemy.name} 造成了 {damage:.2f} 點傷害！")
        elif command == 'H':
            heal = random.random() * max(self.algebra, self.geometry, self.analysis) * 20
            self.health += heal
            print(f"你使用了回血，恢復了 {heal:.2f} 點生命值！")
        elif command == 'R':
            if random.random() < min(self.algebra, self.geometry, self.analysis) / 100:  # 逃跑成功機率與能力值相關
                print(f"{self.name} 選擇了逃跑，戰鬥結束。")
                return
            else:
                print(f"{self.name} 選擇了逃跑，但是逃跑失敗了！")
        else:
            print("無效的指令，請重新輸入。")
        
        damage_to_player = random.random() * 20  # 敵人對玩家造成的傷害
        self.health -= damage_to_player
        print(f"{enemy.name} 對你造成了 {damage_to_player:.2f} 點傷害！")
        print(f"你的生命值剩下 {self.health:.2f} 點，{enemy.name} 的生命值剩下 {enemy.health:.2f} 點。")

if __name__ == "__main__":
    # 測試角色系統
    with open('professor.json', 'r', encoding='utf-8') as f:
        prof_data = json.load(f)

    with open('boss.json', 'r', encoding='utf-8') as f:
        boss_data = json.load(f)

    prof = [professor(p) for p in prof_data['professors']]
    boss_1 = boss(random.choice(boss_data['bosses']))
    player_1 = player("小明", "男")

    for _ in range(10):
        prof_ = random.choice(prof)
        player_1.talk(prof_)
    
    while boss_1.health > 0 and player_1.health > 0:
        player_1.battle(boss_1)