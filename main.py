import pygame, random, time, math, struct
pygame.init()
pygame.mixer.init()

W,H=400,700
WIN=pygame.display.set_mode((W,H))
clock=pygame.time.Clock()

def make_sound(freq, duration_ms, volume=0.3, type="sine"):
    try:
        rate=22050
        n=int(rate*duration_ms/1000)
        buf=bytearray()
        for i in range(n):
            t=i/rate
            if type=="sine": s=math.sin(2*math.pi*freq*t)
            elif type=="square": s=1 if math.sin(2*math.pi*freq*t)>0 else -1
            else: s=random.uniform(-1,1)
            s*= (1 - i/n)
            sample=int(s*32767*volume)
            buf+=struct.pack('<h', sample)*2
        return pygame.mixer.Sound(buffer=bytes(buf))
    except: return None

shoot_sound = make_sound(800, 80, 0.3, "square")
explosion_sound = make_sound(100, 200, 0.4, "noise")
stage_sound = make_sound(400, 400, 0.4, "sine")
win_sound = make_sound(600, 1000, 0.4, "sine")
lose_sound = make_sound(150, 800, 0.4, "sine")
def play(s):
    if s:
        try: s.play()
        except: pass

font=pygame.font.SysFont(None, 40)
big=pygame.font.SysFont(None, 60)
small=pygame.font.SysFont(None, 25)
stage_names=["","SPACE ROCKS","ALIEN ZONE","MINE FIELD","COMET STORM","FINAL BOSS"]
stage_bg=[(0,0,0),(10,10,30),(0,20,10),(30,0,0),(20,0,30),(0,0,0)]

def show_stage(s):
    play(stage_sound)
    WIN.fill((0,0,0))
    WIN.blit(big.render(f"STAGE {s}", True, (255,255,255)),(100, H//2-80))
    pygame.draw.line(WIN,(255,255,255),(20,H//2-10),(W-20,H//2-10),4)
    WIN.blit(font.render(stage_names[s], True, (255,255,0)),(50, H//2+20))
    pygame.display.flip()
    pygame.time.delay(1500)

# OUTER REPLAY LOOP
while True:
    ship_x,ship_y=W//2,H//2
    bullets=[]; enemies=[]; score=0; stage=1
    STAGE_TIME = 40
    show_stage(1)
    stage_start_time = time.time()
    shoot=0; failed=False; running=True

    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); exit()
            if e.type==pygame.MOUSEMOTION and e.buttons[0]: ship_x,ship_y=e.pos
            if e.type==pygame.MOUSEBUTTONDOWN: ship_x,ship_y=e.pos
        if ship_x<20: ship_x=20
        if ship_x>W-20: ship_x=W-20
        if ship_y<20: ship_y=20
        if ship_y>H-20: ship_y=H-20

        elapsed = time.time() - stage_start_time
        if elapsed >= STAGE_TIME:
            stage+=1
            if stage>5: running=False; break
            show_stage(stage)
            enemies=[]; bullets=[]
            stage_start_time = time.time()

        shoot+=1
        if shoot>6:
            bullets.append([ship_x-12, ship_y-5])
            bullets.append([ship_x, ship_y-18])
            bullets.append([ship_x+12, ship_y-5])
            play(shoot_sound); shoot=0

        if stage==1: spawn_chance,size=0.94,20
        elif stage==2: spawn_chance,size=0.90,24
        elif stage==3: spawn_chance,size=0.85,35
        elif stage==4: spawn_chance,size=0.80,42
        else: spawn_chance,size=0.70,50

        if random.random()>spawn_chance:
            enemies.append([random.randint(20,W-20), -30, 2+stage*0.5, size, stage])
            if stage>=3 and random.random()>0.5:
                enemies.append([random.randint(20,W-20), -30, 2+stage*0.5, size, stage])
            if stage==5 and random.random()>0.6:
                enemies.append([random.randint(20,W-20), -30, 2+stage*0.5, size, stage])

        WIN.fill(stage_bg[stage])
        for b in bullets[:]:
            b[1]-=10
            if b[1]<0: bullets.remove(b)
            else: pygame.draw.circle(WIN,(0,255,255),(int(b[0]),int(b[1])),5)
        for en in enemies[:]:
            en[1]+=en[2]
            if en[1]>H+60: enemies.remove(en); continue
            x,y,sz,st=en[0],en[1],en[3],en[4]
            if st==1: pygame.draw.circle(WIN,(150,150,150),(int(x),int(y)),sz)
            elif st==2: pygame.draw.polygon(WIN,(50,255,80),[(x,y-sz//2),(x-sz,y+sz//2),(x+sz,y+sz//2)])
            elif st==3: pygame.draw.rect(WIN,(255,50,50),(x-sz//2,y-sz//2,sz,sz))
            elif st==4: pygame.draw.polygon(WIN,(180,80,255),[(x,y-sz//2),(x+sz//2,y),(x,y+sz//2),(x-sz//2,y)])
            else: pygame.draw.circle(WIN,(255,200,0),(int(x),int(y)),sz)
            if abs(x-ship_x)<25+sz//3 and abs(y-ship_y)<25+sz//3: failed=True; running=False; break
            for b in bullets[:]:
                if abs(b[0]-x)<sz//2+8 and abs(b[1]-y)<sz//2+8:
                    if b in bullets: bullets.remove(b)
                    if en in enemies: enemies.remove(en)
                    play(explosion_sound); score+=10; break

        pygame.draw.rect(WIN,(0,200,255),(ship_x-14, ship_y-5, 28, 20))
        pygame.draw.rect(WIN,(100,220,255),(ship_x-12, ship_y-15, 6, 15))
        pygame.draw.rect(WIN,(100,220,255),(ship_x-3, ship_y-22, 6, 22))
        pygame.draw.rect(WIN,(100,220,255),(ship_x+6, ship_y-15, 6, 15))
        pygame.draw.circle(WIN,(255,255,0),(ship_x-9, ship_y-15),4)
        pygame.draw.circle(WIN,(255,255,0),(ship_x, ship_y-22),4)
        pygame.draw.circle(WIN,(255,255,0),(ship_x+9, ship_y-15),4)
        WIN.blit(font.render(f"S{stage} {score}",True,(255,255,255)),(10,10))
        WIN.blit(small.render(f"Time: {int(STAGE_TIME-elapsed)}s",True,(255,255,100)),(10,45))
        pygame.display.flip()

    # END SCREEN WITH REPLAY / QUIT
    if failed: play(lose_sound)
    else: play(win_sound)

    waiting=True
    while waiting:
        clock.tick(60)
        if failed:
            WIN.fill((80,0,0))
            WIN.blit(big.render("GAME OVER",True,(255,50,50)),(60,H//2-100))
            WIN.blit(font.render(f"Stage {stage} Score {score}",True,(255,255,255)),(50,H//2-40))
        else:
            WIN.fill((0,80,0))
            WIN.blit(big.render("YOU WIN!",True,(50,255,80)),(80,H//2-100))
            WIN.blit(font.render(f"5 STAGES CLEARED!",True,(255,255,255)),(60,H//2-40))

        pygame.draw.line(WIN,(255,255,255),(20,H//2-10),(W-20,H//2-10),3)
        pygame.draw.rect(WIN,(0,180,0),(40, H//2+30, 150, 50))
        pygame.draw.rect(WIN,(180,0,0),(210, H//2+30, 150, 50))
        WIN.blit(font.render("REPLAY",True,(255,255,255)),(60, H//2+42))
        WIN.blit(font.render("QUIT",True,(255,255,255)),(250, H//2+42))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); exit()
            if e.type==pygame.MOUSEBUTTONDOWN:
                x,y=e.pos
                if 40<=x<=190 and H//2+30<=y<=H//2+80:
                    waiting=False # REPLAY
                if 210<=x<=360 and H//2+30<=y<=H//2+80:
                    pygame.quit(); exit()