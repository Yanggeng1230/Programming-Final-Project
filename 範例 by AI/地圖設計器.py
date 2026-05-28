import tkinter as tk
from tkinter import simpledialog
import json

class MapEditor:
    def __init__(self, root, rows=3, cols=3):
        self.root = root
        self.root.title("校園地圖編輯器")
        self.rows = rows
        self.cols = cols
        
        self.locations = {} # 儲存地點 { (r, c): "名稱" }
        self.buttons = {}   # 儲存按鈕元件
        
        # 建立網格按鈕
        self.create_grid()
        
        # 建立匯出按鈕
        export_btn = tk.Button(root, text="匯出地圖為 JSON", command=self.export_json, bg="lightblue")
        export_btn.grid(row=self.rows, column=0, columnspan=self.cols, pady=10, sticky="ew")

    def create_grid(self):
        for r in range(self.rows):
            for c in range(self.cols):
                # 建立按鈕，點擊時觸發 set_location
                btn = tk.Button(self.root, text="(空)", width=10, height=3, 
                                command=lambda r=r, c=c: self.set_location(r, c))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[(r, c)] = btn

    def set_location(self, r, c):
        # 彈出輸入框讓使用者輸入地點名稱
        current_name = self.locations.get((r, c), "")
        new_name = simpledialog.askstring("設定地點", f"請輸入 ({r}, {c}) 的地點名稱：", initialvalue=current_name)
        
        if new_name is not None: # 如果不是按取消
            new_name = new_name.strip()
            if new_name:
                self.locations[(r, c)] = new_name
                self.buttons[(r, c)].config(text=new_name, bg="lightgreen")
            else:
                # 如果輸入空白，則清除該地點
                self.locations.pop((r, c), None)
                self.buttons[(r, c)].config(text="(空)", bg="SystemButtonFace")

    def export_json(self):
        # 整理成我們之前定義的 JSON 格式
        map_data = {
            "width": self.cols,
            "height": self.rows,
            "locations": [],
            "walls": [] # 這裡為了簡化，預設先不匯出牆壁，您可以後續手動添加或擴充程式
        }
        
        for (r, c), name in self.locations.items():
            map_data["locations"].append({
                "pos": [r, c],
                "name": name
            })
            
        json_str = json.dumps(map_data, ensure_ascii=False, indent=2)
        print("\n=== 產生的 JSON 資料 ===")
        print(json_str)
        print("========================\n")
        print("您可以將上述 JSON 複製並存成 map.json")

if __name__ == "__main__":
    root = tk.Tk()
    # 你可以在這裡更改網格大小，例如 MapEditor(root, rows=5, cols=5)
    app = MapEditor(root, rows=3, cols=3) 
    root.mainloop()