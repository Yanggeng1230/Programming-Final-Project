import pygame
import sys
import json
import random
# 引入你寫好的模組
from character import player, professor, boss

# --- 1. 遊戲狀態全面定義 ---
STATE_START_NAME = 0
STATE_START_SEX = 1
STATE_MAP = 2
STATE_TALK = 3
STATE_BATTLE = 4
STATE_DEFEAT = 5
STATE_GAME_OVER = 6 # 新增：徹底遊戲結束狀態

# --- 2. 地圖類別 ---
class GameMap:
    def __init__(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.locations = {}
        self.max_c = data['width'] - 1
        self.max_r = data['height'] - 1

        for loc in data['locations']:
            r, c = loc['pos']
            self.locations[(r, c)] = loc['name']

        self.connections = {}
        for r in range(self.max_r + 1):
            for c in range(self.max_c + 1):
                self.connections[(r, c)] = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr <= self.max_r and 0 <= nc <= self.max_c:
                        self.connections[(r, c)].append((nr, nc))

        for wall in data['walls']:
            r1, c1 = wall['from']
            r2, c2 = wall['to']
            if (r2, c2) in self.connections.get((r1, c1), []):
                self.connections[(r1, c1)].remove((r2, c2))
            if (r1, c1) in self.connections.get((r2, c2), []):
                self.connections[(r2, c2)].remove((r1, c1))

def get_distance(pos1, pos2):
    return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))

def draw_centered_text(screen, text, font, color, y_offset):
    """輔助函式：在螢幕中央渲染文字"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + y_offset))
    screen.blit(text_surface, text_rect)

# --- 3. 戰鬥回合邏輯運算 ---
def execute_battle_turn(p1, b1, cmd, multiplier):
    logs = []
    battle_over = False
    escaped = False

    if cmd == 'A':
        damage = p1.algebra * random.random() * (20 if b1.field == "Algebra" else 10)
        b1.health -= damage
        logs.append(f"你使用了代數之力，對 {b1.name} 造成了 {damage:.2f} 點傷害！")
    elif cmd == 'G':
        damage = p1.geometry * random.random() * (20 if b1.field == "Geometry" else 10)
        b1.health -= damage
        logs.append(f"你使用了幾何之力，對 {b1.name} 造成了 {damage:.2f} 點傷害！")
    elif cmd == 'N':
        damage = p1.analysis * random.random() * (20 if b1.field == "Analysis" else 10)
        b1.health -= damage
        logs.append(f"你使用了分析之力，對 {b1.name} 造成了 {damage:.2f} 點傷害！")
    elif cmd == 'H':
        heal = random.random() * max(p1.algebra, p1.geometry, p1.analysis) * 20
        p1.health += heal
        logs.append(f"你使用了回血，恢復了 {heal:.2f} 點生命值！")
    elif cmd == 'R':
        if random.random() < min(p1.algebra, p1.geometry, p1.analysis) / 100:
            logs.append("逃跑成功！你成功甩開了怨靈。")
            escaped = True
            battle_over = True
            return logs, battle_over, escaped
        else:
            logs.append("逃跑失敗！怨靈攔截了你的去路！")

    if b1.health <= 0:
        logs.append(f"你成功擊敗了怨靈 {b1.name}！")
        battle_over = True
        return logs, battle_over, escaped

    damage_to_player = random.random() * 20 * multiplier
    p1.health -= damage_to_player
    logs.append(f"{b1.name} 發動攻擊，對你造成了 {damage_to_player:.2f} 點傷害！")

    if p1.health <= 0:
        battle_over = True

    return logs, battle_over, escaped

# --- 4. 視窗對話文字產生器 ---
def generate_talk_lines(p1, prof):
    lines = [f"【與 {prof.name} 教授對話中】"]
    if prof.affinity < 30:
        lines.append(f"{prof.name}：同學你是新來的吧？叫什麼名字？")
        lines.append(f"{p1.name}：我叫 {p1.name}。")
        lines.append("你向教授自我介紹，親密度增加了！")
        prof.affinity += 10
    else:
        subj = random.choice(prof.subjects)
        lines.append(f"{prof.name}：{p1.name}，找我有什麼事嗎？")
        lines.append(f"{p1.name}：我想請教一些關於 {subj} 的問題。")
        lines.append("教授很樂意幫助你，親密度增加了！")
        prof.affinity += random.random() * 10
        upgrade = random.random() * prof.affinity / 10
        if prof.field == "Algebra":
            p1.algebra += upgrade
            lines.append(f"你的代數能力增加了！")
        elif prof.field == "Geometry":
            p1.geometry += upgrade
            lines.append(f"你的幾何能力增加了！")
        elif prof.field == "Analysis":
            p1.analysis += upgrade
            lines.append(f"你的分析能力增加了！")
    return lines


def main():
    g_map = GameMap('maps/Gongguan_campus.json')
    
    pygame.init()
    pygame.key.set_repeat(300, 150)
    pygame.key.start_text_input()
    
    TILE_SIZE = 40
    STATUS_BAR_HEIGHT = 60
    
    screen_width = (g_map.max_c + 1) * TILE_SIZE
    screen_height = STATUS_BAR_HEIGHT + (g_map.max_r + 1) * TILE_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("期末專題")
    
    font = pygame.font.SysFont(["microsoftjhenghei", "simhei", "arial"], 16)
    font_large = pygame.font.SysFont(["microsoftjhenghei", "simhei", "arial"], 20)

    p1 = None
    b1 = None
    active_profs = []
    spawn_point = None
    boss_data = None 
    boss_multiplier = 1
    
    player_deaths = 0 
    
    all_positions = list(g_map.locations.keys())
    non_dorm_positions = [pos for pos, name in g_map.locations.items() if "舍" not in name]

    game_state = STATE_START_NAME
    player_name = ""
    player_sex = ""
    input_buffer = ""

    talk_lines = []
    battle_logs = []
    current_talking_prof = None

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.TEXTINPUT:
                if game_state == STATE_START_NAME:
                    input_buffer += event.text
            
            elif event.type == pygame.KEYDOWN:
                if game_state == STATE_START_NAME:
                    if event.key == pygame.K_RETURN:
                        if input_buffer.strip():
                            player_name = input_buffer.strip()
                            input_buffer = ""
                            pygame.key.stop_text_input()
                            game_state = STATE_START_SEX
                    elif event.key == pygame.K_BACKSPACE:
                        input_buffer = input_buffer[:-1]

                elif game_state == STATE_START_SEX:
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        player_sex = "男"
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        player_sex = "女"
                    
                    if player_sex:
                        p1 = player(player_name, player_sex)
                        p1.map = g_map
                        dorm_locations = [pos for pos, name in g_map.locations.items() if ("男二舍" in name if p1.sex == "男" else "女二舍" in name)]
                        if not dorm_locations: dorm_locations = all_positions
                        spawn_point = random.choice(dorm_locations)
                        p1.position = spawn_point

                        with open('professor.json', 'r', encoding='utf-8') as f: prof_data = json.load(f)
                        with open('boss.json', 'r', encoding='utf-8') as f: boss_data = json.load(f)

                        num_profs = min(4, len(prof_data['professors']))
                        selected_profs = random.sample(prof_data['professors'], num_profs)

                        for p_info in selected_profs:
                            prof = professor(p_info)
                            prof.position = random.choice(all_positions)
                            active_profs.append(prof)

                        b1 = boss(random.choice(boss_data['bosses']))
                        b1.position = random.choice(non_dorm_positions)
                        
                        game_state = STATE_MAP

                elif game_state == STATE_MAP:
                    if event.key in [pygame.K_w, pygame.K_UP]: p1.move('w')
                    elif event.key in [pygame.K_s, pygame.K_DOWN]: p1.move('s')
                    elif event.key in [pygame.K_a, pygame.K_LEFT]: p1.move('a')
                    elif event.key in [pygame.K_d, pygame.K_RIGHT]: p1.move('d')
                    elif event.key == pygame.K_f:
                        if b1.health > 0 and get_distance(p1.position, b1.position) <= 1:
                            game_state = STATE_BATTLE
                            battle_logs = [f"遭遇怨靈 {b1.name} ！"]
                        else:
                            for prof in active_profs:
                                if get_distance(p1.position, prof.position) <= 1:
                                    current_talking_prof = prof
                                    talk_lines = generate_talk_lines(p1, prof)
                                    game_state = STATE_TALK
                                    break

                elif game_state == STATE_TALK:
                    if event.key == pygame.K_f:
                        if current_talking_prof:
                            current_talking_prof.position = random.choice(all_positions)
                        game_state = STATE_MAP
                        current_talking_prof = None

                elif game_state == STATE_BATTLE:
                    cmd = None
                    if event.key == pygame.K_a: cmd = 'A'
                    elif event.key == pygame.K_g: cmd = 'G'
                    elif event.key == pygame.K_n: cmd = 'N'
                    elif event.key == pygame.K_h: cmd = 'H'
                    elif event.key == pygame.K_r: cmd = 'R'
                    
                    if cmd:
                        new_logs, over, escaped = execute_battle_turn(p1, b1, cmd, boss_multiplier)
                        battle_logs = new_logs
                        
                        if over:
                            if escaped:
                                game_state = STATE_MAP
                            elif p1.health <= 0:
                                player_deaths += 1
                                if player_deaths >= 3:
                                    game_state = STATE_GAME_OVER
                                else:
                                    game_state = STATE_DEFEAT
                            elif b1.health <= 0:
                                boss_multiplier *= 2
                                b1 = boss(random.choice(boss_data['bosses']))
                                b1.health *= boss_multiplier
                                b1.position = random.choice(non_dorm_positions)
                                game_state = STATE_MAP

                elif game_state == STATE_DEFEAT:
                    if event.key == pygame.K_f:
                        p1.health = 100
                        p1.position = spawn_point
                        
                        b1 = boss(random.choice(boss_data['bosses']))
                        b1.health *= boss_multiplier
                        b1.position = random.choice(non_dorm_positions)
                        
                        game_state = STATE_MAP
                        
                elif game_state == STATE_GAME_OVER:
                    if event.key == pygame.K_ESCAPE:
                        running = False

        # --- 畫面彩繪渲染系統 ---
        if game_state == STATE_START_NAME:
            screen.fill((45, 52, 54))
            draw_centered_text(screen, "期末專題", font_large, (116, 185, 255), -60)
            draw_centered_text(screen, "請輸入你的姓名，並按 [Enter] 鍵確定：", font, (255, 255, 255), -10)
            pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 20, 300, 40))
            draw_centered_text(screen, input_buffer + "|", font, (255, 234, 167), 40)

        elif game_state == STATE_START_SEX:
            screen.fill((45, 52, 54))
            draw_centered_text(screen, "【 選擇角色性別 】", font_large, (116, 185, 255), -60)
            draw_centered_text(screen, f"你好，{player_name}！請選擇你的性別：", font, (255, 255, 255), -10)
            draw_centered_text(screen, "男生：按 [1]", font, (129, 236, 236), 30)
            draw_centered_text(screen, "女生：按 [2]", font, (255, 118, 117), 70)

        elif game_state == STATE_DEFEAT:
            screen.fill((194, 54, 22)) 
            draw_centered_text(screen, "你死了", font_large, (255, 255, 255), -60)
            draw_centered_text(screen, f"你還有 {3 - player_deaths} 次重生機會！", font, (241, 242, 246), -10)
            draw_centered_text(screen, "按 [ F ] 鍵 重生", font, (255, 234, 167), 85)
            
        elif game_state == STATE_GAME_OVER:
            screen.fill((45, 52, 54))
            draw_centered_text(screen, " 遊戲結束 ", font_large, (235, 77, 75), -60)
            draw_centered_text(screen, f"你的分數為：{(p1.algebra+p1.geometry+p1.analysis):.2f}", font, (116, 185, 255), 25)
            draw_centered_text(screen, "按 [ Esc ] 鍵退出遊戲", font, (178, 190, 195), 85)

        elif game_state in [STATE_MAP, STATE_TALK, STATE_BATTLE]:
            screen.fill((240, 240, 240))

            # 1. 繪製狀態列背景
            pygame.draw.rect(screen, (45, 52, 54), pygame.Rect(0, 0, screen_width, STATUS_BAR_HEIGHT))
            
            # 2. 繪製左側玩家屬性
            lives_left = 3 - player_deaths
            p_info_1 = font.render(f"玩家: {p1.name} ({p1.sex}) | HP: {max(0.0, p1.health):.0f}/100 | 生命: {lives_left}", True, (255, 255, 255))
            p_info_2 = font.render(f"【能力】 代數: {p1.algebra:.2f}   幾何: {p1.geometry:.2f}   分析: {p1.analysis:.2f}", True, (116, 185, 255))
            screen.blit(p_info_1, (15, 8))
            screen.blit(p_info_2, (15, 32))

            # 3. 繪製右上角的按鍵功能介紹 (與屬性欄齊平)
            guide_txt1 = font.render("WASD : 移動", True, (255, 234, 167))
            guide_txt2 = font.render("F : 互動", True, (255, 234, 167))
            # 動態計算文字寬度，讓提示靠右對齊 (距離右邊界 15 像素)
            guide_x = screen_width - max(guide_txt1.get_width(), guide_txt2.get_width()) - 15
            screen.blit(guide_txt1, (guide_x, 8))
            screen.blit(guide_txt2, (guide_x, 32))

            # 4. 繪製地圖網格、牆壁與角色
            for r in range(g_map.max_r + 1):
                for c in range(g_map.max_c + 1):
                    map_y = STATUS_BAR_HEIGHT + r * TILE_SIZE
                    rect = pygame.Rect(c * TILE_SIZE, map_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, (210, 210, 210), rect, 1)
                    
                    if (r, c) in g_map.locations:
                        text_surface = font.render(g_map.locations[(r, c)][:2], True, (160, 160, 160))
                        screen.blit(text_surface, (c * TILE_SIZE + 2, map_y + 12))

                    for neighbor in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = r + neighbor[0], c + neighbor[1]
                        if (nr, nc) not in g_map.connections.get((r, c), []):
                            if neighbor == (-1, 0):
                                pygame.draw.line(screen, (235, 77, 75), (c*TILE_SIZE, map_y), ((c+1)*TILE_SIZE, map_y), 3)
                            elif neighbor == (1, 0):
                                pygame.draw.line(screen, (235, 77, 75), (c*TILE_SIZE, map_y+TILE_SIZE), ((c+1)*TILE_SIZE, map_y+TILE_SIZE), 3)
                            elif neighbor == (0, -1):
                                pygame.draw.line(screen, (235, 77, 75), (c*TILE_SIZE, map_y), (c*TILE_SIZE, map_y+TILE_SIZE), 3)
                            elif neighbor == (0, 1):
                                pygame.draw.line(screen, (235, 77, 75), ((c+1)*TILE_SIZE, map_y), ((c+1)*TILE_SIZE, map_y+TILE_SIZE), 3)

            for prof in active_profs:
                prof_y = STATUS_BAR_HEIGHT + prof.position[0] * TILE_SIZE + 20
                pygame.draw.circle(screen, (46, 204, 113), (prof.position[1] * TILE_SIZE + 20, prof_y), 11)
            
            if b1.health > 0:
                boss_y = STATUS_BAR_HEIGHT + b1.position[0] * TILE_SIZE + 20
                pygame.draw.circle(screen, (155, 89, 182), (b1.position[1] * TILE_SIZE + 20, boss_y), 15)
            
            p_y = STATUS_BAR_HEIGHT + p1.position[0] * TILE_SIZE + 20
            pygame.draw.circle(screen, (52, 152, 219), (p1.position[1] * TILE_SIZE + 20, p_y), 12)

            if game_state == STATE_TALK:
                overlay = pygame.Surface((screen_width - 40, 160))
                overlay.set_alpha(230)
                overlay.fill((30, 30, 30))
                screen.blit(overlay, (20, screen_height - 180))
                
                for idx, line in enumerate(talk_lines):
                    color = (116, 185, 255) if "【" in line else (255, 255, 255)
                    txt = font.render(line, True, color)
                    screen.blit(txt, (35, screen_height - 170 + idx * 22))
                
                prompt = font.render("[按 F 鍵 結束談話]", True, (255, 234, 167))
                screen.blit(prompt, (screen_width - 320, screen_height - 45))

            elif game_state == STATE_BATTLE:
                overlay = pygame.Surface((screen_width - 40, 180))
                overlay.set_alpha(235)
                overlay.fill((44, 44, 44))
                screen.blit(overlay, (20, screen_height - 200))
                
                boss_status = font_large.render(f" {b1.name} 的怨靈 | HP: {max(0.0, b1.health):.1f}", True, (250, 177, 160))
                screen.blit(boss_status, (35, screen_height - 192))
                
                for idx, log in enumerate(battle_logs):
                    txt = font.render(log, True, (255, 255, 255))
                    screen.blit(txt, (35, screen_height - 160 + idx * 22))
                
                guide = font.render("戰鬥指令 ➔ [A] 代數之力  [G] 幾何之力  [N] 分析之力  [H] 治療  [R] 撤退", True, (255, 234, 167))
                screen.blit(guide, (35, screen_height - 45))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()