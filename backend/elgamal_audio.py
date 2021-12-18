from backend import stego_audio
import os

upload_folder = "dump"

def is_prima(n):
    found = 0
    if(n > 1):
        for i in range(2, int(n**0.5) + 1):
            if (n % i == 0):
                found = 1
                break
        if (found == 0):
            return True
        else:
            return False
    else:
        return False

def getKunci(p, g, x):
    if(is_prima(p) and p>255):
        if(g < p):
            if(x >= 1 and x<=(p-2)):
                y = (g**x)%p
                return(y,g,x,p)
            else:
                return("Maaf, pilih angka x di antara 1 hingga "+str(p-2))
        else:
            return("Maaf, pilih angka g yang lebih kecil dari p")
    else:
        return ("Maaf, pilih p sebuah bilangan prima dan lebih besar dari 255")

def enkripsi_huruf(m, k, y, g, p):
    a = (g**k)%p
    b = ((y**k)*m) % p
    return str(a)+" "+str(b)

def enkripsi(pesan, k, y, g, p, f):
    if(k < 0 and k >= (p-1)):
        return -1
    else:
        hasil = ""
        for huruf in pesan:
            hasil += str(enkripsi_huruf(ord(huruf), k, y, g, p))
            hasil += " "
        respons = stego_audio.encrypt(os.path.join(upload_folder ,f), 
                                    hasil, 
                                    os.path.join(upload_folder,"enc-"+f))
        return respons

def dekripsi_huruf(a, b, x, p):
    a_x_inverse = a**(p-1-x)
    return ((b*a_x_inverse)%p)

def dekripsi(cipher_file, x, p):
    hasil = ""
    pesan_stego = str(stego_audio.decrypt(cipher_file))
    pesan = pesan_stego.split()
    for i in range (0, len(pesan), 2):
        angkanya = dekripsi_huruf(int(pesan[i]), int(pesan[i+1]), x, p)
        hasil += chr(angkanya)
    return hasil

if __name__ == "__main__":
    p = 2357
    g = 2
    x = 1751
    print(getKunci(p,g,x))
    kunci = getKunci(p,g,x)
    pesannya = "HMMM"
    k = 1520
    # #print("pesannya:",pesannya)
    ciphernya = enkripsi(pesannya, k, kunci[0], kunci[1], kunci[3])
    print("enkripsi:", ciphernya)
    plainnya = dekripsi(ciphernya, kunci[2], kunci[3])
    print("dekripsi:", plainnya)