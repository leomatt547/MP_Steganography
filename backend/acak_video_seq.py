from math import sqrt,log10, ceil
from subprocess import call,STDOUT
import base64
import argparse
import io
import os
import PIL.Image as Image
import numpy as np
import cv2
import shutil
from moviepy.editor import *
import glob
from natsort import natsorted
from os.path import isfile, join
import pathlib

#reference:
# https://github.com/r9ht/Caesar-Cipher-Video-Steganography/blob/a51dae6259192a0fb943215a6c7259a48c574c13/functions.py#L12

def teksToBiner(pesan):
    bits = []
    for i in pesan:
        bits.append(format(ord(i), '08b'))
    return ''.join(bits)

def frame_extract(dir, video):
    temp_folder = dir
    try:
        os.mkdir(temp_folder)
    except OSError:
        remove(temp_folder)
        os.mkdir(temp_folder)
        
    cap = cv2.VideoCapture(video)
    count = 0
    while (cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite(os.path.join(dir, "{:d}.png".format(count)), frame)  # save frame as JPEG file
            count += 1
        else:
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

def changeBit(number, newbit):
    if(number % 2 == 0):
        if(newbit == '0'):
            return number
        else:
            return number + 1
    else:
        if(newbit == '0'):
            return number - 1
        else:
            return number

def convert_frames_to_video(pathIn,pathOut,fps):
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
    #for sorting the file names properly
    files = natsorted(files,reverse=False)
    #files.sort(key = lambda x: int(x[5:-4]))
    for i in range(len(files)):
        if(pathlib.Path(files[i]).suffix == ".png"):
            filename = pathIn + '\\' + files[i]
            #reading each files
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            #inserting the frames into an image array
            frame_array.append(img)
    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'FFV1'), fps, size)
    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])
    out.release()

def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path):
        os.remove(path)  # buang filenya
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("File {} tidak ditemukan.".format(path))

def bacaPesan(pesan):
    A = []
    for i in pesan:
        A.append(format(ord(i), '08b'))
    return A

def stegoing(gambar, key, akhir):
    pesan = bacaPesan(key)
    pixel = iter(gambar)

    for i in range(len(pesan)):
        gambar = [value for value in pixel.__next__()[:3] +
                                pixel.__next__()[:3] +
                                pixel.__next__()[:3]]
        #Sisipkan kode acak/sekuensial pada pixel 0,0
        for j in range(0, 8):
            if (pesan[i][j] == '0' and gambar[j]% 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                gambar[j] -= 1
            elif (pesan[i][j] == '1' and gambar[j] % 2 == 0):
                if(gambar[j] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    gambar[j] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    gambar[j] += 1
        #Dikasih flag di akhir apakah message sudah habis atau belum
        #[bit ke 1-8 (isi pesan), bit ke-9 (flag baca pesan)]
        #FLAG: 1 kalau habis, 0 kalau masih ada
        if ((i == len(pesan) - 1) and akhir):
            if (gambar[-1] % 2 == 0):
                if(gambar[-1] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    gambar[-1] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    gambar[-1] += 1
        else:
            if (gambar[-1] % 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                gambar[-1] -= 1
        
        gambar = tuple(gambar)
        #print(gambar)
        yield gambar[0:3]
        yield gambar[3:6]
        yield gambar[6:9]

def encrypt(dir, pesan):
    print("Mulai ekstraksi...")
    kode = "s" #kode acak
    enc_msg = teksToBiner('s' + pesan + '~#~#!#!#')
    jumlah_frame = len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
    if(len(pesan)>jumlah_frame):
        return (False, '')
    iterator = 0
    psnr_total = 0
    img1 = Image.open(str(dir) +"/" + str(0) + ".png", 'r')
    panjang = img1.size[0]
    lebar = img1.size[1]
    size = panjang * lebar
    for i in range (len(enc_msg)):
        framenumber = i // (3 * size)
        img2 = Image.open(str(dir) +"/" + str(framenumber) + ".png", 'r')
        
        imgbaru = img2.copy()
        
        pixelx = (i % size) // (3 * panjang)
        pixely = ((i % size) % (3 * panjang)) // 3
        pixel = imgbaru.getpixel((pixelx, pixely))
        newpixelr = int(pixel[0])
        newpixelg = int(pixel[1])
        newpixelb = int(pixel[2])
        if (i % 3) == 0:
            newpixelr = changeBit(newpixelr, enc_msg[i])
        elif (i % 3) == 1:
            newpixelg = changeBit(newpixelg, enc_msg[i])
        elif (i % 3) == 2:
            newpixelb = changeBit(newpixelb, enc_msg[i])
        imgbaru.putpixel((pixelx, pixely), (newpixelr, newpixelg, newpixelb))
        
        imgbaru.save(str(dir) +"/" + str(framenumber) + ".png", compress_level = 0)
        if((i % size) == 0):
            a = cv2.imread(str(dir) +"/" + str(framenumber) + ".png")
        elif(((i % size) == size-1) or i == (len(enc_msg) - 1)):
            b = cv2.imread(str(dir) +"/" + str(framenumber) + ".png")
            psnr_total += psnr(a,b)
    frameterganti = ceil(len(enc_msg) / (3 * size))
    strnya = "Nilai PSNR Video adalah: " + str(psnr_total//frameterganti)
    return (True,strnya)

def encrypt_driver(dir, file_name, pesan, output):
    try:
        open(os.path.join(dir,file_name))
    except IOError:
        print(os.path.join(dir,file_name))
        print("Maaf! File tidak ada")
        return -1

    print("Extract Videonya...")
    frame_extract(os.path.join(dir,"temp"), os.path.join(dir,file_name))
    print("Extract Video Selesai")

    ada, respons = encrypt(os.path.join(dir,"temp"), pesan)
    print(ada)
    print(respons)
    if (ada):
        print("Merging Gambarnya...")
        capture = cv2.VideoCapture(os.path.join(dir,str(file_name))) # Stores OG Video into a Capture Window
        fps = capture.get(cv2.CAP_PROP_FPS)
        convert_frames_to_video(os.path.join(dir,"temp/"),os.path.join(dir,"temp","video.avi"),fps)
        #call(["ffmpeg", "-i", "temp/%d.png" , "-vcodec", "png", "temp/video.avi", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT, shell=True)
        #call(["ffmpeg", "-i", "temp/%d.png" , "-vcodec", "png", "temp/video.avi", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT, shell=True)
        print("Merging gambar selesai")

        print("Extract audionya...")
        #call(["ffmpeg", "-i", "citra/" + str(file_name), "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT, shell=True)
        video = VideoFileClip(os.path.join(dir,file_name))
        video.audio.write_audiofile(os.path.join(dir,"temp","audio.mp3"))
        print("Extract Audio Selesai")

        print("Gabung Video dan Audionya")
        #call(["ffmpeg", "-i", "temp/video.mov", "-i", "temp/audio.mp3", "-codec", "copy","citra/enc-" + str(file_name), "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
        call(['ffmpeg',
                '-i', os.path.join(dir,"temp","video.avi"),
                '-i', os.path.join(dir,"temp","audio.mp3"),
                '-y',
                '-vcodec', 'copy',
                '-acodec', 'copy',
                output])
        return respons
    else:
        return -2

def psnr(imageawal,imageakhir):
    rms = np.mean((imageawal - imageakhir) ** 2)
    if (rms == 0):
        return 100
    else:
        return 20*log10(255/rms)

def decrypt(dir):
    video_frame = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    video_frame = file_list_sorted = natsorted(video_frame,reverse=False)
    jumlah_frame = len(video_frame)

    enc_img = Image.open(os.path.join(dir,video_frame[0]),'r')
    biner = ''
    hasil = ''

    panjang = enc_img.size[0]
    lebar = enc_img.size[1]

    typeFlag = ''
    for i in range(3):
        pixel = enc_img.getpixel((0,i))
        newpixelr = int(pixel[0])
        newpixelg = int(pixel[1])
        newpixelb = int(pixel[2])
        typeFlag += str(newpixelr % 2)
        typeFlag += str(newpixelg % 2)
        typeFlag += str(newpixelb % 2)
    
    typeFlag = chr(int(typeFlag[:-1], 2))
    if(typeFlag == 's'):
        print("typeFlag =",typeFlag)
        bytez = []
        found = False
        for i in range(jumlah_frame * panjang * lebar):
            enc_img = Image.open(os.path.join(dir,video_frame[i // (panjang * lebar)]),'r')
            x = (i % jumlah_frame) // panjang
            y = (i % jumlah_frame) % panjang
            pixel = enc_img.getpixel((x,y))
            newpixelr = int(pixel[0])
            newpixelg = int(pixel[1])
            newpixelb = int(pixel[2])
            biner += str(newpixelr % 2)
            biner += str(newpixelg % 2)
            biner += str(newpixelb % 2)
            if i % 8 == 7:
                bytez.append(biner[i-7:i+1])
                hasil += chr(int(bytez[-1], 2))
                if hasil[-8:] == "~#~#!#!#":
                    found = True            
                if found:
                    return hasil[1:-8]

def decrypt_driver(file_name):
    dir = "temp2"
    try:
        open("citra/" + file_name)
    except IOError:
        print("Maaf! File tidak ada")
        exit()
    print("Extract Videonya...")
    frame_extract(dir, os.path.join("citra",str(file_name)))
    print("Extract Video Selesai")

    return decrypt(dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,)
    subparsers = parser.add_subparsers(dest="command")

    encrypt_parser = subparsers.add_parser(
        "encrypt", help=encrypt.__doc__
    )
    encrypt_parser.add_argument("file_input", help='Input Plain File')
    encrypt_parser.add_argument("pesan", help='Input Plain File')

    decrypt_parser = subparsers.add_parser(
        "decrypt", help=decrypt.__doc__
    )
    decrypt_parser.add_argument("file_input", help='Input Plain File')
    #parser.add_argument("command", help='Input command encrypt/decrypt')
    args = parser.parse_args()
    if(args.command == "encrypt"):
        encrypt_driver(args.file_input, args.pesan)
    elif(args.command == "decrypt"):
        print(decrypt_driver(args.file_input))