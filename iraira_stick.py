# ex4から引用

import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


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


class Stumbling_block(pg.sprite.Sprite):
    """
    障害物を生成するクラス
    """

    def __init__(self, xy: tuple[int, int]):
        """
        ブロックをSurfaceを生成
        引数: xy ブロックを配置する座標タプル
        """
        super().__init__()
        self.image = pg.Surface((10, 10))
        pg.draw.rect(self.image, (255, 0, 0), (0, 0, 10, 10))
        self.rect = self.image.get_rect()
        self.rect.center = xy 

    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)

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

    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)

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
    
    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)

class Gimmick_burnar_main(pg.sprite.Sprite):
    """
    バーナーを生成するクラス
    """

    def __init__(self, direct: int, xy: tuple[int, int], life: int):
        super().__init__()
        self.img = pg.image.load(f"fig/beam.png")
        self.size = 1.5
        self.life = life
        if direct == 0:
            self.image = pg.transform.rotozoom(self.img, -90, self.size)
            # gimmicks_bm.add(Gimmick_burnar_main(0, (WIDTH / 3 , HEIGHT / 3 -50)))
            # 上方向の描画
        elif direct == 1:
            self.image = pg.transform.rotozoom(self.img, 0, self.size)
            # gimmicks_bm.add(Gimmick_burnar_main(1, (WIDTH / 3 -50, HEIGHT / 3)))
            # 左方向の描画
        elif direct == 2:
            self.image = pg.transform.rotozoom(self.img, 90, self.size)
            # gimmicks_bm.add(Gimmick_burnar_main(2, (WIDTH / 3, HEIGHT / 3 +50)))
            # 下方向の描画
        elif direct == 3:
            self.image = pg.transform.rotozoom(self.img, 180, self.size)
            # gimmicks_bm.add(Gimmick_burnar_main(3, (WIDTH / 3 +50, HEIGHT / 3)))
            # 右方向の描画
        
        self.rect = self.image.get_rect()
        self.rect.center = xy

    def update(self):
        self.life -= 1
        if self.life < 0:
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

    bird = Bird(3, (900, 400))
    block = pg.sprite.Group()

    gimmicks_ex = pg.sprite.Group()
    gimmicks_bb = pg.sprite.Group()
    gimmicks_bm = pg.sprite.Group()

    # exps = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()

    # burnar_interval = 50  # バーナーが出現するまでの時間
    # burnar_time = 50  # バーナーを出現させる時間

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        screen.blit(bg_img, [0, 0])

        block.add(Stumbling_block((WIDTH / 2, HEIGHT / 2)))

        gimmicks_ex.add(Gimmick_explosion((WIDTH / 2, HEIGHT / 2)))
        gimmicks_bb.add(Gimmick_burnar_base((WIDTH / 3, HEIGHT / 3)))

        # gimmicks_bm.add(Gimmick_burnar_main(0, (WIDTH / 3 , HEIGHT / 3 -50)))
        # gimmicks_bm.add(Gimmick_burnar_main(1, (WIDTH / 3 -50, HEIGHT / 3)))
        # gimmicks_bm.add(Gimmick_burnar_main(2, (WIDTH / 3, HEIGHT / 3 +50)))
        if tmr % 150 == 0:
            gimmicks_bm.add(Gimmick_burnar_main(3, (WIDTH / 3 +50, HEIGHT / 3), 50))        

        if len(pg.sprite.spritecollide(bird, gimmicks_ex, True)) != 0:
            bird.change_explosion(8, screen, 50) # こうかとんを爆発エフェクトに変更
            pg.display.update()
            time.sleep(2)
            return
        
        # if burnar_interval < 0:
        #     """
        #     bunar_intervalが0未満の場合に衝突判定をする
        #     """
        #     if len(pg.sprite.spritecollide(bird, gimmicks_bm, True)) != 0:
        #         bird.change_explosion(8, screen, 50) # こうかとんを爆発エフェクトに変更
        #         pg.display.update()
        #         time.sleep(2)
        #         return

        # for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
        #     exps.add(Explosion(emy, 100))  # 爆発エフェクト
        #     score.value += 10  # 10点アップ
        #     bird.change_img(6, screen)  # こうかとん喜びエフェクト

        # for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
        #     exps.add(Explosion(bomb, 50))  # 爆発エフェクト
        #     score.value += 1  # 1点アップ

        # if len(pg.sprite.spritecollide(bird, bombs, True)) != 0:
        #     bird.change_img(8, screen) # こうかとん悲しみエフェクト
        #     score.update(screen)
        #     pg.display.update()
        #     time.sleep(2)
        #     return

        bird.update(key_lst, screen)
        block.update(screen)
        block.draw(screen)

        gimmicks_ex.update(screen)
        gimmicks_ex.draw(screen)
        gimmicks_bb.update(screen)
        gimmicks_bb.draw(screen)
        
        gimmicks_bm.update()
        gimmicks_bm.draw(screen)
        # burnar_interval -= 1
        # if burnar_interval < 0: 
        #     gimmicks_bm.update(screen)
        #     gimmicks_bm.draw(screen)
        #     burnar_time -= 1
        #     if burnar_time <= 0:
        #         burnar_interval = random.randint(30, 50)
        #         burnar_time = random.randint(30, 50)
        #         continue

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
