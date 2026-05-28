import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os

class CampusMapEditor:
    def __init__(self, root, initial_rows=17, initial_cols=21):
        self.root = root
        self.root.title("校園地圖編輯器 (終極版)")
        
        self.cell_size = 30  # 每個格子的像素大小
        self.locations = {}  # 儲存地點: {(r, c): "名稱"}
        self.walls = set()   # 儲存牆壁: frozenset({(r1, c1), (r2, c2)})
        
        # === 1. 頂部控制面板 (設定行列數) ===
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
        tk.Label(control_frame, text="列數 (Rows / 上下):").grid(row=0, column=0, padx=5)
        self.row_var = tk.IntVar(value=initial_rows)
        tk.Spinbox(control_frame, from_=1, to=20, textvariable=self.row_var, width=5).grid(row=0, column=1, padx=5)
        
        tk.Label(control_frame, text="行數 (Cols / 左右):").grid(row=0, column=2, padx=5)
        self.col_var = tk.IntVar(value=initial_cols)
        tk.Spinbox(control_frame, from_=1, to=20, textvariable=self.col_var, width=5).grid(row=0, column=3, padx=5)
        
        btn_update = tk.Button(control_frame, text="套用網格大小", command=self.apply_grid_size, bg="#f0f0f0")
        btn_update.grid(row=0, column=4, padx=10)

        # === 2. 畫布區域 ===
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(padx=10, pady=5)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # === 3. 底部匯出按鈕 ===
        btn_export = tk.Button(root, text="一鍵匯出 JSON", command=self.export_json, bg="lightblue", font=("Arial", 12, "bold"))
        btn_export.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        # 初始化第一次的網格
        self.apply_grid_size()

    def apply_grid_size(self):
        """套用新的網格大小，並過濾掉越界的資料"""
        self.rows = self.row_var.get()
        self.cols = self.col_var.get()
        
        # 更新畫布大小
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas.config(width=canvas_width, height=canvas_height)
        
        # 過濾掉超出新邊界的地點
        self.locations = {pos: name for pos, name in self.locations.items() 
                          if pos[0] < self.rows and pos[1] < self.cols}
        
        # 過濾掉超出新邊界的牆壁
        valid_walls = set()
        for wall in self.walls:
            cells = list(wall)
            (r1, c1), (r2, c2) = cells[0], cells[1]
            if r1 < self.rows and c1 < self.cols and r2 < self.rows and c2 < self.cols:
                valid_walls.add(wall)
        self.walls = valid_walls
        
        self.redraw()

    def on_click(self, event):
        x, y = event.x, event.y
        c, r = x // self.cell_size, y // self.cell_size
        
        if not (0 <= c < self.cols and 0 <= r < self.rows): return
            
        dx, dy = x % self.cell_size, y % self.cell_size
        margin = 5  # 點擊邊界的容錯距離  
        
        if dx < margin and c > 0: self.toggle_wall((r, c), (r, c - 1))
        elif dx > self.cell_size - margin and c < self.cols - 1: self.toggle_wall((r, c), (r, c + 1))
        elif dy < margin and r > 0: self.toggle_wall((r, c), (r - 1, c))
        elif dy > self.cell_size - margin and r < self.rows - 1: self.toggle_wall((r, c), (r + 1, c))
        else: self.set_location(r, c)

    def toggle_wall(self, cell1, cell2):
        wall = frozenset({cell1, cell2})
        if wall in self.walls: self.walls.remove(wall)
        else: self.walls.add(wall)
        self.redraw()

    def set_location(self, r, c):
        current_name = self.locations.get((r, c), "")
        new_name = simpledialog.askstring("設定地點", f"請輸入 ({r}, {c}) 的地點名稱：\n(留空則清除)", initialvalue=current_name)
        if new_name is not None:
            new_name = new_name.strip()
            if new_name: self.locations[(r, c)] = new_name
            else: self.locations.pop((r, c), None)
            self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if (r, c) in self.locations:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#e0f7fa", outline="lightgray")
                    self.canvas.create_text(x1 + self.cell_size/2, y1 + self.cell_size/2, 
                                            text=self.locations[(r, c)], font=("Arial", 12, "bold"))
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="lightgray", dash=(2, 2))

        for wall in self.walls:
            cells = list(wall)
            (r1, c1), (r2, c2) = cells[0], cells[1]
            if r1 == r2:  
                left_c = min(c1, c2)
                x = (left_c + 1) * self.cell_size
                self.canvas.create_line(x, r1 * self.cell_size, x, (r1 + 1) * self.cell_size, fill="#ff5252", width=6)
            else:         
                top_r = min(r1, r2)
                y = (top_r + 1) * self.cell_size
                self.canvas.create_line(c1 * self.cell_size, y, (c1 + 1) * self.cell_size, y, fill="#ff5252", width=6)

    def export_json(self):
        map_data = {"width": self.cols, "height": self.rows, "locations": [], "walls": []}
        
        for (r, c), name in self.locations.items():
            map_data["locations"].append({"pos": [r, c], "name": name})
            
        for wall in self.walls:
            cells = list(wall)
            map_data["walls"].append({"from": list(cells[0]), "to": list(cells[1])})
            
        # --- 實體檔案儲存邏輯 ---
        # 取得目前 python 檔案所在的資料夾路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "campus_map.json")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(map_data, f, ensure_ascii=False, indent=2)
            
            # 彈出成功提示視窗
            messagebox.showinfo("匯出成功", f"地圖已成功儲存至：\n{file_path}")
        except Exception as e:
            # 防呆：如果有權限問題或其他錯誤
            messagebox.showerror("匯出失敗", f"發生錯誤：\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CampusMapEditor(root)
    root.mainloop()