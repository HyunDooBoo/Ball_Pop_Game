import pygame
import os
import pygame_menu
import random
########################################################################
#기본 초기화 (반드시 해야 함)
pygame.init() #초기화

screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height)) #화면 크기

pygame.display.set_caption("공 맞추기")

#프레임
clock = pygame.time.Clock()

#게임 모드 선택 변수
select = 0

#배경음악
base = pygame.mixer.Sound( "music.mp3" )
base.set_volume(0.01)
base.play(-1)

#효과음
hit_sound = pygame.mixer.Sound("hit.wav")
hit_sound.set_volume(0.1)

rapid_sound = pygame.mixer.Sound("rapid.mp3")
rapid_sound.set_volume(0.02)

double_sound = pygame.mixer.Sound("double.mp3")
double_sound.set_volume(0.02)

bounce_sound = pygame.mixer.Sound("bounce.mp3")
bounce_sound.set_volume(0.08)

shoot_sound = pygame.mixer.Sound("shoot.mp3")
shoot_sound.set_volume(0.02)

break_sound = pygame.mixer.Sound("break.mp3")
break_sound.set_volume(0.1)

#########################################################################

#최고기록 읽어오기 함수
def read_score():
    read = open("bestscore.txt", "r")
    bestscore = int(read.readline())
    read.close
    return bestscore


#최고기록 쓰기 함수
def write(bestscore):
    if int(score) > int(bestscore) :
        bestscore = score
        write = open("bestscore.txt", "w")
        write.write(str(bestscore))
        write.close()

#캐릭터 속도 감소
def character_slow(slow_count,character_speed):
    if slow_count == 15:
        if character_speed == 2:
            return slow_count - 100, character_speed
        else:
            return slow_count - 100, character_speed - 0.5
    else:
        return slow_count, character_speed
    


# 1. 사용자 게임 초기화 (배경 화면, 게임 이미지, 좌표, 속도, 폰트, 시간 등)
def main():
    global score
    score = 0
    bestscore = read_score()
    current_path = os.path.dirname(__file__) #현재 py파일의 위치 반환
    image_path = os.path.join(current_path, "images") #이미지 폴더 위치 반환
    eat_double = 0
    slow_count = 0
    pop_score = 0

    #배경
    cloud = pygame.image.load(os.path.join(image_path,"cloud.png"))
    cloud_x_pos = -1000
    background = pygame.image.load(os.path.join(image_path,"background.png"))

    #발판 만들기
    stage = pygame.image.load(os.path.join(image_path, "stage.png"))
    stage_size = stage.get_rect().size
    stage_height = stage_size[1] #스테이지의 높이만 가져오기

    #풀숲 발판 만들기
    ground = pygame.image.load(os.path.join(image_path, "ground.png"))

    #캐릭터
    character = pygame.image.load(os.path.join(image_path,"character.png"))
    character_size = character.get_rect().size
    character_width = character_size[0]
    character_height = character_size[1]
    character_x_pos = (screen_width/2) - (character_width/2)
    character_y_pos = screen_height - character_height - stage_height

    character_to_x_right = 0
    character_to_x_left = 0

    #플레이어 이속
    character_speed = 5

    #맵 총알 수 제한
    if select == 2:
        max_weapon = 3
    else:
        max_weapon = 1

    #아이템 이동속도
    rapid_x_speed = -3
    rapid_y_speed = 1
    double_x_speed = 3
    double_y_speed = 1

    #아이템 설정
    double = pygame.image.load(os.path.join(image_path,"double.png"))
    double_size = double.get_rect().size
    double_width = double_size[0]
    double_x_pos = random.randint(0,screen_width-double_width)
    double_y_pos = random.randint(0,10)

    rapid = pygame.image.load(os.path.join(image_path,"rapid.png"))
    rapid_size = rapid.get_rect().size
    rapid_width = rapid_size[0]
    rapid_x_pos = random.randint(0,screen_width-rapid_width)
    rapid_y_pos = random.randint(0,10)

    #무기 만들기
    weapon = pygame.image.load(os.path.join(image_path,"weapon.png"))
    weapon_size = weapon.get_rect().size
    weapon_width = weapon_size[0]

    #무기는 한 번에 여러 발 발사 가능
    weapons = []

    #무기 이동 속도
    weapon_speed = 10

    #공 만들기 (4개 크기 따로 처리)
    ball_images = [
        pygame.image.load(os.path.join(image_path,"ballon1.png")),
        pygame.image.load(os.path.join(image_path,"ballon2.png")),
        pygame.image.load(os.path.join(image_path,"ballon3.png")),
        pygame.image.load(os.path.join(image_path,"ballon4.png"))]

    #공 크기별 스피드
    ball_speed_y = [-18, -15, -12, -9]

    #공들
    balls = []

    #첫 공 추가 (제일 큰 공)
    balls.append({
        "pos_x" : random.randint(0,screen_width-160),
        "pos_y" : 50,
        "img_idx" : 0,
        "to_x" : 3,
        "to_y" : -6,
        "init_spd_y" : ball_speed_y[0]})

    #사라질 무기, 공 정보 저장
    weapon_to_remove = -1
    ball_to_remove = -1

    #font
    game_font = pygame.font.Font(None, 40)

    #게임 시간
    if select == 2:
        total_time = 50
    else:
        total_time = 30

    start_ticks = pygame.time.get_ticks()

    #게임 종료 메세지
    game_result = "Game over"

    gamerun = True
    while gamerun:
        dt = clock.tick(40) #초당 프레임 수 설정

        # 2. 이벤트 처리 (키보드, 마우스)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #창 X버튼 누를 시 작동
                gamerun = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    character_to_x_left -= character_speed
                elif event.key == pygame.K_RIGHT:
                    character_to_x_right += character_speed
                elif event.key == pygame.K_SPACE:
                    if len(weapons) >= max_weapon :
                        continue
                    else:
                        weapon_x_pos = character_x_pos + character_width / 2 - weapon_width / 2
                        weapon_y_pos = character_y_pos
                        weapons.append([weapon_x_pos,weapon_y_pos])
                        shoot_sound.play()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    character_to_x_left = 0
                elif event.key == pygame.K_RIGHT:
                    character_to_x_right = 0
            
        # 3. 게임 캐릭터 위치 정의
        character_x_pos += character_to_x_left + character_to_x_right

        if character_x_pos < 0 :
            character_x_pos = 0
        elif character_x_pos > screen_width - character_width:
            character_x_pos = screen_width - character_width

        #아이템 위치 조정
        if double_x_pos <= 0 or double_x_pos > screen_width - double_width:
            double_x_speed = double_x_speed * -1

        if double_y_pos <= 20:
            double_y_speed += 0.06
        else:
            double_y_speed -= 0.06
        
        double_y_pos += double_y_speed
        double_x_pos += double_x_speed

        if rapid_x_pos <= 0 or rapid_x_pos > screen_width - rapid_width:
            rapid_x_speed = rapid_x_speed * -1

        if rapid_y_pos <= 20:
            rapid_y_speed += 0.06
        else:
            rapid_y_speed -= 0.06

        rapid_y_pos += rapid_y_speed
        rapid_x_pos += rapid_x_speed

        #무기 위치 조정
        weapons = [[w[0],w[1] - weapon_speed]for w in weapons] #무기 위치 위로
        
        #천장에 닿은 무기 없애기
        weapons = [ [w[0],w[1] ] for w in weapons if w[1] > -10]


        #공 위치 정의
        for ball_idx, ball_val in enumerate(balls):
            ball_pos_x = ball_val["pos_x"]
            ball_pos_y = ball_val["pos_y"]
            ball_img_idx = ball_val["img_idx"]

            ball_size = ball_images[ball_img_idx].get_rect().size
            ball_width = ball_size[0]
            ball_height = ball_size[1]

            #벽에 닿았을 때 공 위치 변경
            if ball_pos_x <= 0 or ball_pos_x > screen_width - ball_width:
                ball_val["to_x"] = ball_val["to_x"] * -1

            if ball_pos_y >= screen_height - stage_height - ball_height:
                bounce_sound.play()
                ball_val["to_y"] = ball_val["init_spd_y"]
            else:
                ball_val["to_y"] += 0.5

            ball_val["pos_x"] += ball_val["to_x"]
            ball_val["pos_y"] += ball_val["to_y"]
        
        #구름 배경 위치 조정
        cloud_x_pos += 0.3

        # 4. 충돌 처리

        #캐릭터 rect정보 업데이트
        character_rect = character.get_rect()
        character_rect.left = character_x_pos
        character_rect.top = character_y_pos

        #아이템 rect정보 업데이트
        rapid_rect = rapid.get_rect()
        rapid_rect.left = rapid_x_pos
        rapid_rect.top = rapid_y_pos

        double_rect = double.get_rect()
        double_rect.left = double_x_pos
        double_rect.top = double_y_pos

        for ball_idx, ball_val in enumerate(balls):
            ball_pos_x = ball_val["pos_x"]
            ball_pos_y = ball_val["pos_y"]
            ball_img_idx = ball_val["img_idx"]

            #공 rect 정보 업데이트
            ball_rect = ball_images[ball_img_idx].get_rect()
            ball_rect.left = ball_pos_x
            ball_rect.top = ball_pos_y

            #공과 캐릭터 충돌
            if character_rect.colliderect(ball_rect):
                gamerun = False
                break
            
            #공과 무기들 충돌 처리
            for weapon_idx, weapon_val in enumerate(weapons):
                weapon_pos_x = weapon_val[0]
                weapon_pos_y = weapon_val[1]

                weapon_rect = weapon.get_rect()
                weapon_rect.left = weapon_pos_x
                weapon_rect.top = weapon_pos_y

                if weapon_rect.colliderect(rapid_rect):
                    rapid_sound.play()
                    max_weapon = 6
                    rapid_x_pos = -10000
                    del weapons[weapon_idx]

                if weapon_rect.colliderect(double_rect):
                    double_sound.play()
                    eat_double = 1
                    double_x_pos = -10000
                    weapon = pygame.image.load(os.path.join(image_path,"double_shot.png"))
                    del weapons[weapon_idx]

                if weapon_rect.colliderect(ball_rect):
                    hit_sound.play()
                    if select == 2 and ball_img_idx <3:
                        if pop_score == 30: #기록모드일 시 30대 치면 공이 터짐
                            pop_score = 0
                
                            ball_width = ball_rect.size[0]
                            ball_height = ball_rect.size[1]

                            small_ball_rect = ball_images[ball_img_idx + 1].get_rect()
                            small_ball_width = small_ball_rect.size[0]
                            small_ball_height = small_ball_rect.size[0]

                            balls.append({
                                "pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2),
                                "pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2),
                                "img_idx" : ball_img_idx + 1,
                                "to_x" : -3,
                                "to_y" : -6,
                                "init_spd_y" : ball_speed_y[ball_img_idx + 1]})

                            balls.append({
                                "pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2),
                                "pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2),
                                "img_idx" : ball_img_idx + 1,
                                "to_x" : 3,
                                "to_y" : -6,
                                "init_spd_y" : ball_speed_y[ball_img_idx + 1]})

                        else:
                            if eat_double == 1:
                                score += 20
                                slow_count += 1
                                pop_score += 1
                            else:
                                score += 10
                                slow_count += 1
                                pop_score += 1
                            del weapons[weapon_idx]
                            break

                    weapon_to_remove = weapon_idx #해당 무기 없애기 위한 값 설정
                    ball_to_remove = ball_idx #해당 공 없애기 위한 값 설정

                    #가장 작은 공이 아니면 다음 공으로 나누기
                    if select != 2  and ball_img_idx < 3:

                        #현재 공 크기 정보 가지고 오기
                        ball_width = ball_rect.size[0]
                        ball_height = ball_rect.size[1]

                        #나눠진 공 정보
                        small_ball_rect = ball_images[ball_img_idx + 1].get_rect()
                        small_ball_width = small_ball_rect.size[0]
                        small_ball_height = small_ball_rect.size[0]

                        #왼쪽으로 튕겨나가는 작은 공
                        balls.append({
                            "pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2),
                            "pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2),
                            "img_idx" : ball_img_idx + 1,
                            "to_x" : -3,
                            "to_y" : -6,
                            "init_spd_y" : ball_speed_y[ball_img_idx + 1]})

                        #오른쪽 튕기는 공
                        balls.append({
                            "pos_x" : ball_pos_x + (ball_width / 2) - (small_ball_width / 2),
                            "pos_y" : ball_pos_y + (ball_height / 2) - (small_ball_height / 2),
                            "img_idx" : ball_img_idx + 1,
                            "to_x" : 3,
                            "to_y" : -6,
                            "init_spd_y" : ball_speed_y[ball_img_idx + 1]})
                    break
            else:
                continue
            break

        


        #충돌된 공 or 무기 없애기
        if ball_to_remove > -1 :
            break_sound.play()
            del balls[ball_to_remove]
            ball_to_remove = -1

        if weapon_to_remove > -1:
            del weapons[weapon_to_remove]
            weapon_to_remove = -1

        #모든 공 없앨 경우 게임 종료
        if(len(balls)) == 0:
            game_result = "Mission Complete"
            gamerun = False

        # 5. 화면에 그리기
        screen.blit(background,(0,0))
        screen.blit(cloud,(cloud_x_pos,0))
        
        for weapon_x_pos, weapon_y_pos in weapons:
            screen.blit(weapon, (weapon_x_pos, weapon_y_pos))

        for idx, val in enumerate(balls):
            ball_pos_x = val["pos_x"]
            ball_pos_y = val["pos_y"]
            ball_img_idx = val["img_idx"]
            screen.blit(ball_images[ball_img_idx], (ball_pos_x, ball_pos_y))

        screen.blit(ground,(0,screen_height-stage_height-20))
        screen.blit(character,(character_x_pos,character_y_pos))
        screen.blit(stage,(0,screen_height-stage_height))

        #진행 시간
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000
        timer = game_font.render("Time : {}".format(int(total_time - elapsed_time)), True, (21,219,22))
        screen.blit(timer,(10,10))

        #기록모드 전용 점수, 최고기록 표시
        if select == 2 :
            score_image = game_font.render("score : {}".format(score), True, (21,219,22))
            screen.blit(score_image,(10,40))

            bestscore_image = game_font.render("bestscore : {}".format(bestscore), True, (21,219,22))
            screen.blit(bestscore_image,(10,70))       

        #시간 초과
        if total_time - elapsed_time <= 0 :
            game_result = "Time over"
            gamerun = False
        
        #아이템 그리기
        if select != 2:
            rapid_x_pos = -100
            double_x_pos = -100

        screen.blit(rapid,(rapid_x_pos,rapid_y_pos))
        screen.blit(double,(double_x_pos,double_y_pos))
        
        slow_count, character_speed = character_slow(slow_count,character_speed)

        pygame.display.update()

    msg = game_font.render(game_result, True, (255,255,0))
    msg_rect = msg.get_rect(center=(int(screen_width / 2), int(screen_height / 2)))
    screen.blit(msg, msg_rect)
    pygame.display.update()

    write(bestscore)

    pygame.time.delay(2000)

    restart()


#게임 메뉴

def select_mode(value, difficulty):
    global select
    if difficulty == 1:
        select = 1
    elif difficulty == 2:
        select = 2


def gamemenu():
    font = pygame.font.SysFont("malgungothic", 30)
    t = pygame_menu.themes.THEME_BLUE.copy()
    t.widget_font=font
    menu = pygame_menu.Menu("Menu", 500, 300,theme=t)
    menu.add.selector("모드 설정", [("노말모드", 1),("기록모드", 2)],
                      onchange=select_mode)
    menu.add.button("게임 시작", main)
    menu.mainloop(screen)

def restart():
    font = pygame.font.SysFont("malgungothic", 30)
    t = pygame_menu.themes.THEME_BLUE.copy()
    t.widget_font=font
    menu = pygame_menu.Menu("Menu", 500, 300,theme=t)
    menu.add.button("다시 시작", gamemenu)
    menu.add.button("게임 종료", pygame_menu.events.EXIT)
    menu.mainloop(screen)

if __name__ == "__main__":
    gamemenu()