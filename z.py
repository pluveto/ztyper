#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os.path
from dep.playsound import playsound
from dep.keyboard import keyboard
import sys
import os
sys.path.append(os.getcwd())


preventMode = True


def playasync(file):
    if not os.path.isfile(file):
        return

    from platform import system
    if system() == 'Windows':
        playsound.playsound(file, False)
    return


# 缓冲，用于负责处理连续按键的输入
buffer = ""

# 加载键盘映射


def loadConvertMap():
    import csv
    reader = csv.reader(open('convert_map.csv', 'r'))
    d = {}
    for row in reader:
        k, v = row
        d[k] = v
    return d


convertMap = loadConvertMap()

# 当按键被捕获时触发


def trig(data):
    global buffer

    # if len(buffer) == 0:
    #     audioFile = "assets/audio/" + "ds2" + ".wav"
    # else:
    #     audioFile = "assets/audio/" + "f2" + ".wav"

    # if os.path.isfile(audioFile):
    #     playasync(audioFile)

    # 处理特殊指令
    if len(data) > 1:
        # 清空缓冲
        if 'clear buffer' == data:
            buffer = ""
            return
        if 'line break' == data:
            buffer = ""
            handle("cmd line break")
            return
        if 'backspace' == data:
            if(len(buffer) != 0):
                buffer = ""
                return

            handle("cmd backspace")
            return
    # 处理正常输入
    buffer += data
    # 每两个按键为一组
    if(len(buffer) >= 2):
        handle(buffer)
        buffer = ""
    return


def backspace():
    with open("out.txt", 'rb+') as file:
        file.seek(-1, os.SEEK_END)
        if file.tell() == 0:
            return
        file.truncate()

# 处理用户输入的字符组，如 01, 02


def handle(buffer):

    if(len(buffer) > 2):
        if "cmd line break" == buffer:
            result = '\n'
            with open("out.txt", "a") as outputFile:
                outputFile.write(result)
            audioFile = "assets/audio/" + "linebreak" + ".wav"
            playasync(audioFile)
            return
        elif "cmd backspace" == buffer:
            audioFile = "assets/audio/" + "backspace" + ".wav"
            backspace()
            playasync(audioFile)
            return
        return

    if not buffer in convertMap:
        print("unknown: " + buffer)
        audioFile = "assets/audio/" + "unknown" + ".wav"
        playasync(audioFile)
        return

    result = convertMap[buffer]
    if " " == result:
        audioFile = "space"
    elif "linebreak" == result:
        result = "\n"
        audioFile = "linebreak"
    elif "backspace" == result:
        audioFile = "backspace"
        result = ""
        backspace()
    elif "quote" == result:
        result = "\""
        audioFile = "quote"
    elif "," == result:
        audioFile = "comma"
    elif "." == result:
        audioFile = "period"
    else:
        audioFile = result

    audioFile = "assets/audio/" + audioFile + ".wav"

    if(len(result) > 0):

        if preventMode:
            keyboard.write(result)

        print(result)

        with open("out.txt", "a") as outputFile:
            outputFile.write(result)

    playasync(audioFile)
    return

# 绑定键盘监听


def cb(evt):
    print("evt: " + evt.name + " scan: " + str(evt.scan_code))

    if evt.scan_code in [82, 79, 80, 81, 75, 76, 77, 71, 72, 73]:
        name = evt.name
    elif evt.scan_code == 55:
        name = 'clear buffer'
    elif evt.scan_code == 28:  # enter
        name = 'line break'
    elif evt.scan_code == 14:
        name = 'backspace'
    else:
        return
    trig(name)
    with open("out.bin", 'ab') as file:
        file.write(bytes([evt.scan_code]))
    return


def bindKeys():
    if(preventMode):
        keyboard.on_press_key(82, cb, True)
        keyboard.on_press_key(79, cb, True)
        keyboard.on_press_key(80, cb, True)
        keyboard.on_press_key(81, cb, True)
        keyboard.on_press_key(75, cb, True)
        keyboard.on_press_key(76, cb, True)
        keyboard.on_press_key(77, cb, True)
        keyboard.on_press_key(71, cb, True)
        keyboard.on_press_key(72, cb, True)
        keyboard.on_press_key(73, cb, True)

    # keyboard.on_press(cb)
    return


bindKeys()

# Block forever, like `while True`.
keyboard.wait()
