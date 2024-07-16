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
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 1.5)
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
        screen.blit(self.img, self.rect)

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
    # exps = pg.sprite.Group()

                                            # ここが中心
    stage = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
             [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],  # ここが中心
             [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
             [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
             [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],]

    for i in range(len(stage)):
        for j in range(len(stage[i])):
            if stage[i][j] == 1:
                lock_block.add(Stumbling_lock_block((25 + j*50, 25 + i*50), (50, 50)))

    tmr = 0
    clock = pg.time.Clock()
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        screen.blit(bg_img, [0, 0])

        if len(pg.sprite.spritecollide(bird, lock_block, True)) != 0:
            bird.change_explosion(8, screen, 50) # こうかとん悲しみエフェクト
            pg.display.update()
            time.sleep(2)
            return

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
        lock_block.draw(screen)
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
