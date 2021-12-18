import wave

from math import log10
import argparse
import PIL.Image as Image
import numpy as np
import cv2
import os

def bacaPesan(pesan):
    A = []
    for i in pesan:
        A.append(format(ord(i), '08b'))
    return A

def stegoing(gambar, pesan):
    pesan = bacaPesan(pesan)
    pixel = iter(gambar)

    for i in range(len(pesan)):
        tempgambar = [value for value in pixel.__next__()[:3] +
                                pixel.__next__()[:3] +
                                pixel.__next__()[:3]]
        for j in range(0, 8):
            if (pesan[i][j] == '0' and tempgambar[j]% 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                tempgambar[j] -= 1
            elif (pesan[i][j] == '1' and tempgambar[j] % 2 == 0):
                if(tempgambar[j] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    tempgambar[j] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    tempgambar[j] += 1
        #Dikasih flag di akhir apakah message sudah habis atau belum
        #[bit ke 1-8 (isi pesan), bit ke-9 (flag baca pesan)]
        #FLAG: 1 kalau habis, 0 kalau masih ada
        if (i == len(pesan) - 1):
            if (tempgambar[-1] % 2 == 0):
                if(tempgambar[-1] != 0):
                    #Apabila gambar ke i tidak 0 maka kurangi 1 supaya ganjil
                    tempgambar[-1] -= 1
                else:
                    #Apabila gambar ke i bernilai 0 maka tambah 1 supaya ganjil
                    tempgambar[-1] += 1
        else:
            if (tempgambar[-1] % 2 != 0):
                #kurangi 1, karena ganjil dimulai 1 dan tidak mungkin minus
                tempgambar[-1] -= 1
        
        tempgambar = tuple(tempgambar)
        yield tempgambar[0:3]
        yield tempgambar[3:6]
        yield tempgambar[6:9]

def encrypt(file, pesan, output):
    perubahan = 0
    audio = wave.open(file,mode="rb")
    arr_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    string = pesan + int((len(arr_bytes)-(len(pesan)*8*8))/8) * '#'
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in string])))
    for i, bit in enumerate(bits):
        arr_bytes[i] = (arr_bytes[i] & 254) | bit
        perubahan += 1
    arr_bytes_baru = bytes(arr_bytes)
    audiobaru =  wave.open(output, 'wb')
    audiobaru.setparams(audio.getparams())
    audiobaru.writeframes(arr_bytes_baru)
    audiobaru.close()
    audio.close()

    if (perubahan>0):
        strnya = "Nilai PSNR adalah: " + str(psnr(perubahan, len(arr_bytes_baru)))
    else:
        strnya = -2
    return str(strnya)

def psnr(perubahan,jumlah_frame):
    rms = perubahan/jumlah_frame
    return 20*log10(8/rms)

def decrypt(file):
    pesan = ""
    audio = wave.open(file, mode='rb')
    arr_bytes = bytearray(list(audio.readframes(audio.getnframes())))
    bits = [arr_bytes[i] & 1 for i in range(len(arr_bytes))]
    string = "".join(chr(int("".join(map(str,bits[i:i+8])),2)) for i in range(0,len(bits),8))
    pesan = string.split("###")[0]
    audio.close()	
    return pesan

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,)
    subparsers = parser.add_subparsers(dest="command")

    encrypt_parser = subparsers.add_parser(
        "encrypt", help=encrypt.__doc__
    )
    encrypt_parser.add_argument("file_input", help='Input Plain File')
    encrypt_parser.add_argument("pesan", help='Input File yang ingin disisipkan')
    encrypt_parser.add_argument("output", help='Masukkan nama dir output stego')

    decrypt_parser = subparsers.add_parser(
        "decrypt", help=decrypt.__doc__
    )
    decrypt_parser.add_argument("file_input", help='Input Stego File')
    args = parser.parse_args()
    if(args.command == "encrypt"):
        encrypt(args.file_input, args.pesan, args.output)
    elif(args.command == "decrypt"):
        print(decrypt(args.file_input))
