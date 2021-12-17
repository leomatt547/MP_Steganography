#python stego_video.py encrypt test.avi Leonard

from math import sqrt,log10
from subprocess import call,STDOUT
import argparse
import os
import PIL.Image as Image
import numpy as np
import cv2
import shutil
from moviepy.editor import *
from natsort import natsorted
from os.path import isfile, join
import pathlib

#reference:
# https://github.com/r9ht/Caesar-Cipher-Video-Steganography/blob/a51dae6259192a0fb943215a6c7259a48c574c13/functions.py#L12

def pisahteks(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))

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

def convert_frames_to_video(pathIn,pathOut,fps):
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
    #for sorting the file names properly
    files = natsorted(files,reverse=False)
    size = (0,0)
    for i in range(len(files)):
        if(pathlib.Path(files[i]).suffix == ".png"):
            filename = pathIn + files[i] 
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
        yield gambar[0:3]
        yield gambar[3:6]
        yield gambar[6:9]

def encrypt(dir, pesan):
    print("Mulai ekstraksi...")
    panjang_pesan=100
    
    pesannya =  pisahteks(pesan+"ÿ",panjang_pesan)
    jumlah_frame = len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])
    if(len(pesannya)>jumlah_frame):
        return False
    iterator = 0

    psnr_total = 0
    for i in range (len(pesannya)):
        img2 = Image.open(str(dir) +"/" + str(i) + ".png", 'r')
        img = img2.getdata()
        if (len(pesannya[i]) == 0):
            return (False, "pesannya kosong")
        imgbaru = img2.copy()
        panjang = imgbaru.size[0]
        lebar = imgbaru.size[1]
        (x, y) = (0, 0)

        if(i == len(pesannya)-1):
            akhir = True
        else:
            akhir = False

        for pixel in stegoing(img, pesannya[i], akhir):
            imgbaru.putpixel((x, y), pixel)
            if (x == lebar - 1):
                x = 0
                y += 1
            else:
                x += 1
        a = cv2.imread(str(dir) +"/" + str(i) + ".png")
        imgbaru.save(str(dir) +"/" + str(i) + ".png", compress_level = 0)
        b = cv2.imread(str(dir) +"/" + str(i) + ".png")
        psnr_total += psnr(a,b)
        iterator += 1
    strnya = "Nilai PSNR Video adalah:" + str(psnr_total//iterator)
    return (True, strnya)

def encrypt_driver(dir, file_name, pesan):
    output = os.path.join(dir, "enc-"+file_name)
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
    if (ada):
        print("Merging Gambarnya...")
        capture = cv2.VideoCapture(os.path.join(dir,str(file_name))) # Stores OG Video into a Capture Window
        fps = capture.get(cv2.CAP_PROP_FPS)
        convert_frames_to_video(os.path.join(dir,"temp/"),os.path.join(dir,"temp","video.avi"),fps)
        print("Merging gambar selesai")

        print("Extract audionya...")
        video = VideoFileClip(os.path.join(dir,file_name))
        video.audio.write_audiofile(os.path.join(dir,"temp","audio.mp3"))
        print("Extract Audio Selesai")

        print("Gabung Video dan Audionya")
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
    return 20*log10(255/rms)

def decrypt(dir):
    pesan = ''

    video_frame = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    video_frame = natsorted(video_frame,reverse=False)

    # string of binary citra
    teksbinary = ''

    k = 0
    while(True):
        frame_selesai = False
        img = video_frame[k]
        img2 = Image.open(str(dir) +"/" + img , 'r')
        gambar = img2.getdata()
        pesan_per_frame = 0
        pixel = iter(gambar)

        while(frame_selesai == False):
            gambar = [value for value in pixel.__next__()[:3] +
                                pixel.__next__()[:3] +
                                pixel.__next__()[:3]]
            # string of binary citra
            teksbinary = ''
            for i in gambar[:8]:
                if (i % 2 == 0):
                    teksbinary += '0'
                else:
                    teksbinary += '1'
            if (teksbinary == "11111111"):
                frame_selesai == True
                return pesan
            pesan += chr(int(teksbinary, 2))
            pesan_per_frame += 1
            if(pesan_per_frame>=100):
                frame_selesai == True
                break
        k += 1

def decrypt_driver(dir, file_name):
    try:
        open(os.path.join(dir,file_name))
    except IOError:
        return -1
    print("Extract Videonya...")
    frame_extract(os.path.join(dir,"temp2"), os.path.join(dir,str(file_name)))
    print("Extract Video Selesai")

    pesan = decrypt(os.path.join(dir,"temp2"))
    return pesan

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
    args = parser.parse_args()
    if(args.command == "encrypt"):
        encrypt_driver("dump", args.file_input, args.pesan)
    elif(args.command == "decrypt"):
        print(decrypt_driver("dump", args.file_input))