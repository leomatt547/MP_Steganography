import cv2
import PIL.Image as Image
from math import sqrt,log10
import numpy as np
import argparse

def teksToBiner(pesan):
    bits = []
    for i in pesan:
        bits.append(format(ord(i), '08b'))
    return ''.join(bits)

def binerToTeks(biner):
    return ''.join(chr(int(biner[8*i:8*i+8], 2))  for i in range(len(biner)//8))

def psnr(imageawal,imageakhir):
    rms = np.mean((cv2.imread(imageawal) - cv2.imread(imageakhir)) ** 2)
    return 20*log10(255/rms)

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

def encrypt(image, pesan, output):
    img = Image.open(image, 'r')
    enc_img = img.copy()
    enc_msg = teksToBiner('s' + pesan + '~#~#!#!#')
    panjang = enc_img.size[0]
    lebar = enc_img.size[1]
    for i in range(0, len(enc_msg), 3):
        x = (i//3) // panjang
        y = (i//3) % panjang
        pixel = enc_img.getpixel((x,y))
        newpixelr = int(pixel[0])
        newpixelg = int(pixel[1])
        newpixelb = int(pixel[2])
        newpixelr = changeBit(newpixelr, enc_msg[i])
        if(i+1 < len(enc_msg)):
            newpixelg = changeBit(newpixelg, enc_msg[i + 1])
        if(i+2 < len(enc_msg)):
            newpixelb = changeBit(newpixelb, enc_msg[i + 2])
        enc_img.putpixel((x,y), (newpixelr, newpixelg, newpixelb))
        print(newpixelr, newpixelg, newpixelb)
    #enc_img_name = image[:-4] + '_enciphered' + image[-4:]
    #enc_img.save(enc_img_name)
    enc_img.convert('RGB').save(output)
    strnya = "Nilai PSNR adalah:" + str(psnr(image,output))
    return strnya

def decrypt(image):
    enc_img = Image.open(image, 'r')
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
        for x in range(panjang):
            for y in range(lebar):
                pixel = enc_img.getpixel((x,y))
                newpixelr = int(pixel[0])
                newpixelg = int(pixel[1])
                newpixelb = int(pixel[2])
                biner += str(newpixelr % 2)
                biner += str(newpixelg % 2)
                biner += str(newpixelb % 2)
        bytez = [biner[i:i+8] for i in range(0, len(biner), 8)]

        found = False
        for byte in bytez:
            hasil += chr(int(byte, 2))
            if hasil[-8:] == "~#~#!#!#":
                found = True
                break
        if found:
            return hasil[1:-8]

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
        encrypt(args.file_input, args.pesan)
    elif(args.command == "decrypt"):
        print(decrypt(args.file_input))