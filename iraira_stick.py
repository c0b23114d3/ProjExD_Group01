# ex4から引用

import math
import os
import random
import sys
import time
import pygame as pg

pg.init()


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ

os.chdir(os.path.dirname(os.path.abspath(__file__)))

titel_screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption("イライラスティック")

title_font = pg.font.SysFont(None,64) #タイトルのフォントサイズ
text_font = pg.font.SysFont(None,36)  #システムのフォントサイズ

title_text = title_font.render("iraira stick",True, (255,255,255)) #タイトルのテキスト
start_text = text_font.render('Enter start' ,True,(255,255,255))   #始める時のテキスト
end_text = text_font.render('Esc end',True,(255,255,255))          #終わるときのテキスト

#タイトル画面のループ
start = True
while start:
    for botan in pg.event.get():
        if botan.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif botan.type == pg.KEYDOWN:
            if botan.key == pg.K_RETURN:#enterでゲーム開始
                start = False
            elif botan.key == pg.K_ESCAPE:#escでゲーム終了
                pg.quit()
                sys.exit()
    
    titel_screen.fill((101,187,233))#タイトルの背景の色
    titel_screen.blit(title_text,(WIDTH//2 - title_text.get_width()//2,100))#タイトルの描写
    titel_screen.blit(start_text,(WIDTH//2 - start_text.get_width()//2,300))#始める時のテキストの描写
    titel_screen.blit(end_text,(WIDTH//2 - end_text.get_width()//2,350))    #終わる時のテキストの描写
    pg.display.flip()#画面の更新



    






def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)

    def change_explosion(self, num: int, screen: pg.Surface, life: int):
        self.img = pg.image.load(f"fig/explosion.gif")
        self.timg = pg.transform.flip(self.img, False, True)
        screen.blit(self.img, self.rect)
        screen.blit(self.timg, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
                
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)


class Stumbling_lock_block(pg.sprite.Sprite):
    """
    固定された障害物を生成するクラス
    """

    def __init__(self, xy: tuple[int, int], size: tuple[int, int]):
        """
        ブロックをSurfaceを生成
        引数: xy ブロックを配置する座標タプル
        """
        super().__init__()
        self.image = pg.Surface(size)
        pg.draw.rect(self.image, (255, 0, 0), (0, 0, size[0], size[1]))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = xy

    def update(self):
        pass

class Gimmick_explosion(pg.sprite.Sprite):
    """
    地雷を生成するクラス
    """
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((50, 50))
        pg.draw.circle(self.image, (232, 143, 186), (25, 25), 20)
        self.rect = self.image.get_rect()
        self.rect.center = xy

    def update(self):
        pass

class Gimmick_burnar_base(pg.sprite.Sprite):
    """
    バーナーを設置するための土台を生成するクラス    
    """
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((50, 50))
        pg.draw.circle(self.image, (0, 0, 255), (25, 25), 20)
        self.rect = self.image.get_rect()
        self.rect.center = xy
    
    def update(self):
        pass

class Gimmick_burnar_main(pg.sprite.Sprite):
    """
    バーナーを生成するクラス
    """

    def __init__(self, direct: int, gimmick_block: Gimmick_burnar_base, life: int):
        super().__init__()
        self.size = 1.5
        self.life = life
        self.img = pg.image.load(f"fig/beam.png")
        burnarx = 0
        burnary = 0

        
        # 上方向の描画
        if direct == 0:
            self.image = pg.transform.rotozoom(self.img, -90, self.size)
            self.rect = self.image.get_rect()
            burnary -= self.rect.height / 2
            
        # 左方向の描画
        elif direct == 1:
            self.image = pg.transform.rotozoom(self.img, 0, self.size)
            self.rect = self.image.get_rect()
            burnarx -= self.rect.width / 2
            
        # 下方向の描画
        elif direct == 2:
            self.image = pg.transform.rotozoom(self.img, 90, self.size)
            self.rect = self.image.get_rect()
            burnary += self.rect.height / 2
        
        # 右方向の描画
        elif direct == 3:
            self.image = pg.transform.rotozoom(self.img, 180, self.size)
            self.rect = self.image.get_rect()
            burnarx += self.rect.width / 2

        self.rect.centerx = gimmick_block.rect.centerx + burnarx
        self.rect.centery = gimmick_block.rect.centery + burnary
        
    def update(self):
        self.life -= 1
        if self.life < 0:
            self.kill()

class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    引数：画像をゲーム画面に表示する基底クラス
    """
    imgs = [pg.image.load(f"fig/alien{i}.png") for i in range(1, 4)]

    def __init__(self):
        super().__init__()
        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(WIDTH + 20, WIDTH + 100), random.randint(0, HEIGHT)
            
        self.speed = random.randint(3, 10)
    
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

# class Explosion(pg.sprite.Sprite):
#     """
#     爆発に関するクラス
#     """
#     def __init__(self, obj: "Bomb|Enemy", life: int):
#         """
#         爆弾が爆発するエフェクトを生成する
#         引数1 obj：爆発するBombまたは敵機インスタンス
#         引数2 life：爆発時間
#         """
#         super().__init__()
#         img = pg.image.load(f"fig/explosion.gif")
#         self.imgs = [img, pg.transform.flip(img, 1, 1)]
#         self.image = self.imgs[0]
#         self.rect = self.image.get_rect(center=obj.rect.center)
#         self.life = life

#     def update(self):
#         """
#         爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
#         爆発エフェクトを表現する
#         """
#         self.life -= 1
#         self.image = self.imgs[self.life//10%2]
#         if self.life < 0:
#             self.kill()



def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/pg_bg.jpg")

    bird = Bird(3, (50, 550))
    lock_block = pg.sprite.Group()
    emys = pg.sprite.Group()

    gimmicks_ex = pg.sprite.Group()
    gimmicks_bb = pg.sprite.Group()
    gimmicks_bm = pg.sprite.Group()

    # exps = pg.sprite.Group()

                                            # ここが中心
    stage = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
             [1, 0, 0, 2, 1, 1, 1, 1, 1, 1, 2, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 2, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 2, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],  # ここが中心
             [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 2, 1, 1, 1, 1, 1, 2, 0, 0, 0, 1],
             [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 1],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],]

    for i in range(len(stage)):
        for j in range(len(stage[i])):
            if stage[i][j] == 1:
                lock_block.add(Stumbling_lock_block((25 + j*50, 25 + i*50), (50, 50)))
            elif stage[i][j] == 2:
                gimmicks_ex.add(Gimmick_explosion((25 + j*50, 25 + i*50)))
            elif stage[i][j] == 3:
                gimmicks_bb.add(Gimmick_burnar_base((25 + j*50, 25 + i*50)))

    # exps = pg.sprite.Group()
    tmr = 0
    clock = pg.time.Clock()
    # game_now = True

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        screen.blit(bg_img, [0, 0])

        # if len(pg.sprite.spritecollide(bird, lock_block, True)) != 0:
        #     bird.change_explosion(8, screen, 50)
        #     pg.display.update()
        #     time.sleep(2)
        #     return
        
        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())

        for emys in pg.sprite.spritecollide(bird, emys, True):
            bird.change_explosion(8, screen, 50) #こうかとんを爆発エフェクトに変更
            pg.display.update()
            time.sleep(2)
            return

        # 150フレームに1回バーナーを出現させる
        if tmr % 150 == 0:
            for burnar in gimmicks_bb:
                gimmicks_bm.add(Gimmick_burnar_main(1, burnar, 50))        

        if len(pg.sprite.spritecollide(bird, gimmicks_ex, True)) != 0:
            bird.change_explosion(8, screen, 50) # こうかとんを爆発エフェクトに変更
            pg.display.update()
            time.sleep(2)
            return
        

        if len(pg.sprite.spritecollide(bird, lock_block, True)) != 0: # 失敗時
            bird.change_explosion(8, screen, 50)
            pg.display.update()
            time.sleep(1)
            imgfail = pg.image.load(f"fig/gameover.jpg")
            screen.blit(imgfail, [WIDTH/2, HEIGHT/2])
            pg.display.update()
            time.sleep(2)
            return
        
        # if len(pg.sprite.spritecollide(bird, item, True)) != 0: # クリア時
        #     bird.change_img(9, screen)
        #     pg.display.update()
        #     time.sleep(1)
        #     imgclear = pg.image.load(f"fig/clear.jpg")
        #     screen.blit(imgclear, [400, 200])
        #     time.sleep(2)
        #     return

        bird.update(key_lst, screen)
        lock_block.draw(screen)
        emys.update()
        emys.draw(screen)
        gimmicks_ex.draw(screen)
        gimmicks_bb.draw(screen)
        
        gimmicks_bm.update()
        gimmicks_bm.draw(screen)
        # exps.update()
        # exps.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()