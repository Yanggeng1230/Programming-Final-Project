import random
import 範例.fake_map as fake_map

class GridGame:
    def __init__(self, m, n):
        self.m = m  # 列數 (Rows)
        self.n = n  # 行數 (Cols)
        
        # 使用字典記錄每個格子「可以通往」的相鄰格子
        # 格式: {(r, c): set((nr, nc), (nr, nc)...)}
        self.connections = {(r, c): set() for r in range(m) for c in range(n)}
        
        # 玩家初始位置 (左上角)
        self.player_pos = (0, 0)
        # 終點位置 (右下角)
        self.exit_pos = (m - 1, n - 1)

    def remove_wall(self, cell1, cell2):
        """移除兩個相鄰方格之間的牆壁 (建立雙向通道)"""
        self.connections[cell1].add(cell2)
        self.connections[cell2].add(cell1)

    def generate_maze(self):
        """使用深度優先搜尋 (DFS) 生成一個保證有解的隨機迷宮"""
        visited = set()
        stack = [(0, 0)]
        visited.add((0, 0))

        while stack:
            current = stack[-1]
            r, c = current
            
            # 找出尚未訪問過的合法相鄰格子 (上下左右)
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.m and 0 <= nc < self.n and (nr, nc) not in visited:
                    neighbors.append((nr, nc))

            if neighbors:
                # 隨機選擇一個相鄰格子打通牆壁
                next_cell = random.choice(neighbors)
                self.remove_wall(current, next_cell)
                visited.add(next_cell)
                stack.append(next_cell)
            else:
                # 如果四周都走過了，就退回上一格
                stack.pop()

    def display(self):
        """在終端機中印出目前的迷宮狀態與玩家位置"""
        print("\n" + "遊戲開始！使用 W/A/S/D 移動，尋找右下角的出口。" )
        # 繪製迷宮頂部邊界
        print("+" + "---+" * self.n)
        
        for r in range(self.m):
            row_str = "|"
            bottom_str = "+"
            for c in range(self.n):
                # 判斷當前格子顯示什麼 (玩家 P，終點 E，或空白)
                if self.player_pos == (r, c):
                    row_str += " P "
                elif self.exit_pos == (r, c):
                    row_str += " E "
                else:
                    row_str += "   "

                # 判斷右側是否有牆壁
                if (r, c + 1) in self.connections[(r, c)]:
                    row_str += " "  # 沒牆壁，印空格
                else:
                    row_str += "|"  # 有牆壁，印直線

                # 判斷下方是否有牆壁
                if (r + 1, c) in self.connections[(r, c)]:
                    bottom_str += "   +" # 沒牆壁，通道打開
                else:
                    bottom_str += "---+" # 有牆壁，印橫線

            print(row_str)
            print(bottom_str)

    def move(self, direction):
        """處理玩家的移動請求"""
        r, c = self.player_pos
        # 定義移動方向的座標變化
        moves = {'w': (-1, 0), 's': (1, 0), 'a': (0, -1), 'd': (0, 1)}

        if direction in moves:
            dr, dc = moves[direction]
            next_pos = (r + dr, c + dc)

            # 核心判斷：目標格子是否存在於「當前格子的可通行列表」中
            if next_pos in self.connections[(r, c)]:
                self.player_pos = next_pos
                print("➡️ 移動成功！")
            else:
                print("❌ 撞到牆壁或邊界了！無法往該方向移動。")
        else:
            print("⚠️ 無效的輸入。請輸入 w/a/s/d。")


# === 遊戲主迴圈 ===
if __name__ == "__main__":
    # 建立一個 5x6 的方格地圖
    game = GridGame(5, 6) 
    # 隨機打通牆壁生成地圖
    game.generate_maze()  

    while True:
        game.display()
        
        # 檢查是否抵達終點
        if game.player_pos == game.exit_pos:
            print("\n🎉 恭喜你抵達終點，遊戲通關！ 🎉")
            break

        # 獲取玩家輸入
        cmd = input("\n請輸入移動方向 (w=上, s=下, a=左, d=右, q=離開): ").strip().lower()
        
        if cmd == 'q':
            print("遊戲結束。")
            break
            
        game.move(cmd)