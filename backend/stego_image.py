from math import log10
import argparse
import PIL.Image as Image
import numpy as np
import cv2
import os

#python acak.py encrypt ./lena.bmp 1leomaumakan
#python acak.py decrypt ./stegonya.png
def bacaPesan(pesan):
    A = []
    for i in pesan:
        A.append(format(ord(i), '08b'))
    return A
    # f = open(input_file,'rb')
    # l = f.read(1)
    # while l:
    #     A.append(format(int.from_bytes(l, "big"), '08b'))
    #     l = f.read(1)
    # f.close()

def stegoing(gambar, pesan):
    pesan = bacaPesan(pesan)
    pixel = iter(gambar)
    #print("baca pesan",pesan)

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
    img = Image.open(file, 'r')
    #print(str(os.path.getsize(file)))
    # if (os.path.getsize(pesan) <= 0):
    #     raise ValueError('File data yang ingin disisipkan kosong')
    # elif(os.path.getsize(pesan) > 0.001 * os.path.getsize(file)):
    #     raise ValueError('Maaf, file data yang ingin disisipkan lebih besar dari file stegonya')
    if (len(pesan) <= 0):
        raise ValueError('File data yang ingin disisipkan kosong')
    elif(len(pesan) > os.path.getsize(file)):
        raise ValueError('Maaf, file data yang ingin disisipkan lebih besar dari file stegonya')
    
    imgbaru = img.copy()
    panjang = imgbaru.size[0]
    lebar = imgbaru.size[1]
    (x, y) = (0, 0)

    for pixel in stegoing(imgbaru.getdata(), pesan):
        imgbaru.putpixel((x, y), pixel)
        if (x == panjang - 1):
            x = 0
            y += 1
        else:
            x += 1
    imgbaru.convert('RGB').save(output)
    strnya = "Nilai PSNR adalah: " + str(psnr(cv2.imread(file),cv2.imread(output)))
    print(strnya)
    return str(output)

def psnr(imageawal,imageakhir):
    rms = np.mean((imageawal - imageakhir) ** 2)
    return 20*log10(255/rms)

def decrypt(file):
    img = Image.open(file, 'r')
    imgdata = iter(img.getdata())
    pesan = ""
 
    #f = open(output_file, 'wb')
    while (True):
        pixel = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
 
        # string of binary data
        teksbin = ''
 
        for i in pixel[:8]:
            if (i % 2 == 0):
                teksbin += '0'
            else:
                teksbin += '1'

        pesan += chr(int(teksbin, 2))
        #f.write(int(teksbin, 2).to_bytes(1, 'big'))
        if (pixel[-1] % 2 != 0):
            #f.close()
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
    #parser.add_argument("command", help='Input command encrypt/decrypt')
    args = parser.parse_args()
    if(args.command == "encrypt"):
        encrypt(args.file_input, args.file_pesan, args.output)
    elif(args.command == "decrypt"):
        print(decrypt(args.file_input))