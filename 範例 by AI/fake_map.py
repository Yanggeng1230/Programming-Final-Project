import json

class CampusMap:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.connections = {}
        self.poi = {} # Point of Interest (地點名稱)

    def load_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.width = data['width']
        self.height = data['height']
        
        # 初始化所有格子為「全通」，之後再根據 walls 移除
        for r in range(self.height):
            for c in range(self.width):
                self.connections[(r, c)] = set()
                # 預設與四周相連 (邊界除外)
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        self.connections[(r, c)].add((nr, nc))

        # 根據 walls 資訊「切斷」連線
        for wall in data['walls']:
            u = tuple(wall['from'])
            v = tuple(wall['to'])
            if v in self.connections[u]: self.connections[u].remove(v)
            if u in self.connections[v]: self.connections[v].remove(u)

        # 載入地點名稱
        for loc in data['locations']:
            self.poi[tuple(loc['pos'])] = loc['name']

    def get_location_name(self, pos):
        return self.poi.get(pos, "走廊")
    
    def display(self):
        """將校園地圖渲染在終端機上"""
        print("+" + "---+" * self.width)
        
        for r in range(self.height):
            row_str = "|"
            bottom_str = "+"
            for c in range(self.width):
                # 處理格子內容：如果有地點名稱，取第一個中文字顯示
                loc_name = self.poi.get((r, c), "")
                if loc_name:
                    cell_content = f" {loc_name[0]} "
                else:
                    cell_content = "   "
                row_str += cell_content
                
                # 判斷右側是否有牆壁 (檢查 (r, c) 是否能通往 (r, c+1))
                if (r, c + 1) in self.connections[(r, c)]:
                    row_str += " "  # 沒牆壁
                else:
                    row_str += "|"  # 有牆壁
                    
                # 判斷下方是否有牆壁 (檢查 (r, c) 是否能通往 (r+1, c))
                if (r + 1, c) in self.connections[(r, c)]:
                    bottom_str += "   +" # 沒牆壁，通道打開
                else:
                    bottom_str += "---+" # 有牆壁，印橫線
                    
            print(row_str)
            print(bottom_str)
    
if __name__ == "__main__":
    campus_map = CampusMap()
    campus_map.load_from_json('fake_map.json')
    print(f"地圖大小：{campus_map.width}x{campus_map.height}")
    print("格子連線情況：")
    for cell, neighbors in campus_map.connections.items():
        print(f"  {cell} -> {neighbors}")
    print("地點名稱：")
    for pos, name in campus_map.poi.items():
        print(f"  {pos} : {name}")
    campus_map.display()