import os
import subprocess
import redis
from flask import Flask, render_template, request
from flask import redirect, url_for
from flask import make_response



app = Flask(__name__)
app.debug = True



def makeFontAwesome(icon_name, color="black"):
        """
        font awesome のunicodeから画像生成
        色の指定可能
        生成画像サイズは400x400
        戻り値は画像の名前(相対パス名)
        """
        icon = 'printf "{}" | '.format(icon_name)
        cmd = "convert "
        o_size = "-size 400x400 "
        o_background = '-background "none" -fill {} '.format(color)
        o_font = "-font static/fonts/fontawesome-webfont.ttf "
        o_point = "-pointsize 200 "
        o_gravity = "-gravity center label:@- "
        o_out = "static/photo/temp/{}.png".format(icon_name)

        cmd = icon + cmd + o_size + o_background + o_font + o_point + o_gravity + o_out

        res = subprocess.call(cmd, shell=True)

        if res == 0:
            return o_out
        else:
            try:
                raise ValueError("I couldn't make image !!")
            except ValueError as e:
                print(e)


def insertWords(image, words, color="black", font="Meiryo", size="50"):
        """
        画像に文字を挿入
        色とフォントと文字サイズの指定可能
        挿入位置は画像下中央から10px上
        """
        cmd = "convert "
        o_point = "-pointsize {} ".format(size)
        o_font = "-font {} ".format(font)
        o_gravity = "-gravity south "
        o_annotate = '-annotate +0+10 "{}" '.format(words)
        o_fill = '-fill {} '.format(color)
        o_in = "{} ".format(image)
        o_out = "{}".format(image)

        cmd = cmd + o_point + o_gravity + o_font + o_annotate + o_fill + o_in + o_out

        res = subprocess.call(cmd, shell=True)

        if res == 0:
            return o_out
        else:
            try:
                raise ValueError("I couldn't make image !!")
            except ValueError as e:
                print(e)


def overlayImage(bottom_img, top_img, gravity="center", geometry=(5, 5)):
    """
    2つの画像の合成
    bottom_imgの上にtop_imgを乗せる
    """
    cmd = "convert " + bottom_img + " " + top_img + " "
    o_gravity = "-gravity {} ".format(gravity)
    o_geometry = "-geometry +{0[0]}+{0[1]} ".format(geometry)
    o_compose = "-compose over "
    o_composite = "-composite {}".format(bottom_img)

    cmd += o_gravity + o_geometry + o_compose + o_composite

    res = subprocess.call(cmd, shell=True)

    if res == 0:
        return bottom_img
    else:
        try:
            raise ValueError("I couldn't make image !!")
        except ValueError as e:
            print(e)


def makeBackground(name="menu", color="DodgerBlue"):
    name = "static/photo/richmenu/" + name + ".png"

    res = subprocess.call("convert -size 1200x810 xc:white {}".format(name), shell=True)

    drawStroke(name, coords=(0, 0, 1200, 0), color=color, width=26)
    drawStroke(name, coords=(0, 810, 1200, 810), color=color, width=26)

    if res == 0:
        return "{}".format(name)
    else:
        try:
            raise ValueError("I couldn't make image !!")
        except ValueError as e:
            print(e)


def drawStroke(image, coords=(0, 0, 0, 0), color="black", width=1):
    """
    幅と色指定のできる線描画関数
    """
    cmd = "convert "
    o_color = "-stroke {} ".format(color)
    o_width = "-strokewidth {} ".format(width)
    o_draw = '-draw "line {0[0]},{0[1]} {0[2]},{0[3]}" '.format(coords)

    cmd = cmd + image + " " + o_color + o_width + o_draw  + image
    print(cmd)

    res = subprocess.call(cmd, shell=True)
    print(res)

    if res == 0:
        return image
    else:
        try:
            raise ValueError("I couldn't make image !!")
        except ValueError as e:
            print(e)


POSITION = {"nw": (0, 5), 
            "n": (400, 5),
            "ne": (800, 5),
            "sw": (0, 405),
            "s": (400, 405),
            "se": (800, 405)
            }


mb = " "


@app.route("/", methods=["GET"])
def fontawesome():
    global mb
    if request.args.get("name"):
        name = request.args.get("name")
        color = request.args.get("color")
        mb = makeBackground(name, color)
        overlayImage(mb, "static/photo/background.png", gravity="northwest", geometry=(0,13))

        for dirct, geom in POSITION.items():
            fa = request.args.get("{}_icon".format(dirct))
            fa = "\\u" + fa
            fa = fa.encode("utf-8")
            fa = fa.decode("unicode-escape")
            fa_color = request.args.get("{}_color".format(dirct))
            fa_words = request.args.get("{}_words".format(dirct))
            mfa = makeFontAwesome(fa, fa_color)
            mfa = insertWords(mfa, fa_words)
            overlayImage(mb, mfa, gravity="northwest", geometry=geom)

        return redirect(url_for("showPhoto"))
    else:
        return render_template("login.html")


@app.route("/showPhoto")
def showPhoto():
    global mb
    subprocess.call("rm static/photo/temp/* ", shell=True)
    return render_template("showPhoto.html", image=mb)



if __name__ == "__main__":
    app.run()
