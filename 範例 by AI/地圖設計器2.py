import tkinter as tk
from tkinter import simpledialog
import json

class CampusMapEditor:
    def __init__(self, root, rows=4, cols=4):
        self.root = root
        self.root.title("校園地圖編輯器 (進階版)")
        self.rows = rows
        self.cols = cols
        
        # 設定每個方格的像素大小
        self.cell_size = 80  
        
        self.locations = {}  # 儲存地點: {(r, c): "名稱"}
        self.walls = set()   # 儲存牆壁: 格式為 frozenset({(r1, c1), (r2, c2)}) 以確保無方向性
        
        # 建立畫布 (Canvas)
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)
        
        # 綁定滑鼠左鍵點擊事件
        self.canvas.bind("<Button-1>", self.on_click)
        
        # 建立匯出按鈕
        btn_export = tk.Button(root, text="匯出地圖為 JSON", command=self.export_json, bg="lightblue", font=("Arial", 12))
        btn_export.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 初始繪製
        self.redraw()

    def on_click(self, event):
        """處理滑鼠點擊事件"""
        x, y = event.x, event.y
        
        # 計算點擊落在哪個格子內
        c = x // self.cell_size
        r = y // self.cell_size
        
        # 防呆：確保點擊在有效網格內
        if not (0 <= c < self.cols and 0 <= r < self.rows):
            return
            
        # 計算在格子內的相對座標
        dx = x % self.cell_size
        dy = y % self.cell_size
        
        # 設定「判定為邊界」的像素範圍 (距離邊緣 15 像素內算點擊邊界)
        margin = 15  
        
        # 判斷點擊位置，決定行為
        if dx < margin and c > 0:
            # 點擊左側邊界 -> 切換與左方格子的牆壁
            self.toggle_wall((r, c), (r, c - 1))
        elif dx > self.cell_size - margin and c < self.cols - 1:
            # 點擊右側邊界 -> 切換與右方格子的牆壁
            self.toggle_wall((r, c), (r, c + 1))
        elif dy < margin and r > 0:
            # 點擊上方邊界 -> 切換與上方格子的牆壁
            self.toggle_wall((r, c), (r - 1, c))
        elif dy > self.cell_size - margin and r < self.rows - 1:
            # 點擊下方邊界 -> 切換與下方格子的牆壁
            self.toggle_wall((r, c), (r + 1, c))
        else:
            # 點擊中心區域 -> 設定地點名稱
            self.set_location(r, c)

    def toggle_wall(self, cell1, cell2):
        """切換兩格之間的牆壁狀態"""
        # 使用 frozenset 讓 {(0,0), (0,1)} 和 {(0,1), (0,0)} 視為同一道牆
        wall = frozenset({cell1, cell2})
        if wall in self.walls:
            self.walls.remove(wall) # 已經有牆就拆除
        else:
            self.walls.add(wall)    # 沒有牆就建立
        self.redraw()

    def set_location(self, r, c):
        """設定地點名稱"""
        current_name = self.locations.get((r, c), "")
        new_name = simpledialog.askstring("設定地點", f"請輸入 ({r}, {c}) 的地點名稱：\n(留空則清除)", initialvalue=current_name)
        
        if new_name is not None:
            new_name = new_name.strip()
            if new_name:
                self.locations[(r, c)] = new_name
            else:
                self.locations.pop((r, c), None) # 留白就刪除地點
            self.redraw()

    def redraw(self):
        """重新繪製整個畫布"""
        self.canvas.delete("all")
        
        # 1. 畫基本網格與地點
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                if (r, c) in self.locations:
                    # 有地點的格子填上淺藍色
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#e0f7fa", outline="lightgray")
                    # 寫上地點名稱
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, 
                                            text=self.locations[(r, c)], font=("Arial", 12, "bold"))
                else:
                    # 空白的格子
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="lightgray", dash=(2, 2))

        # 2. 畫牆壁 (紅色粗線)
        for wall in self.walls:
            cells = list(wall)
            (r1, c1), (r2, c2) = cells[0], cells[1]
            
            if r1 == r2:  
                # 水平相鄰 (畫垂直的牆壁)
                left_c = min(c1, c2)
                x = (left_c + 1) * self.cell_size
                y1 = r1 * self.cell_size
                y2 = (r1 + 1) * self.cell_size
                self.canvas.create_line(x, y1, x, y2, fill="#ff5252", width=6)
            else:         
                # 垂直相鄰 (畫水平的牆壁)
                top_r = min(r1, r2)
                x1 = c1 * self.cell_size
                x2 = (c1 + 1) * self.cell_size
                y = (top_r + 1) * self.cell_size
                self.canvas.create_line(x1, y, x2, y, fill="#ff5252", width=6)

    def export_json(self):
        """匯出符合我們遊戲格式的 JSON"""
        map_data = {
            "width": self.cols,
            "height": self.rows,
            "locations": [],
            "walls": []
        }
        
        for (r, c), name in self.locations.items():
            map_data["locations"].append({"pos": [r, c], "name": name})
            
        for wall in self.walls:
            cells = list(wall)
            map_data["walls"].append({
                "from": list(cells[0]),
                "to": list(cells[1])
            })
            
        json_str = json.dumps(map_data, ensure_ascii=False, indent=2)
        print("\n" + "="*30)
        print(json_str)
        print("="*30 + "\n")
        print("💡 您可以將上述 JSON 複製，貼到您的 map.json 檔案中供遊戲讀取！")

if __name__ == "__main__":
    root = tk.Tk()
    # 您可以在這裡自由修改地圖大小，例如 (root, rows=6, cols=6)
    app = CampusMapEditor(root, rows=4, cols=4)
    root.mainloop()