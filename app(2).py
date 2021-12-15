from flask import *
from cipher import rc4
from StegoAcak import acakgambar, acakvideo
from StegoSekuensial import acak_gambar_seq,acak_video_seq
from werkzeug.utils import secure_filename
import urllib.request
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["UPLOAD_FOLDER"]='dump'
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS_CITRA = set(['png', 'bmp'])
ALLOWED_EXTENSIONS_VIDEO = set(['avi'])

@app.route('/')
def home():
    return render_template("home.html")

#--------------------RC4----------------------------

@app.route('/rc4')
def rc4_page():
    return render_template("rc4.html")

@app.route('/rc4/encrypt')
def rc4_encrypt():
    plaintext = request.args.get("text")
    key = request.args.get("key")
    return rc4.encrypt_text(plaintext, key)

@app.route('/rc4/decrypt')
def rc4_decrypt():
    ciphertext = request.args.get("text")
    key = request.args.get("key")
    return rc4.decrypt_text(ciphertext, key)

@app.route('/rc4/file_encrypt', methods=["POST"])
def rc4_encrypt_file():
    if request.method == 'POST':
        key = request.form.get("key")
        f = request.files['file']
        f.save("dump/input")
        f = open(f"dump/input", "rb")
        plain = f.read()
        cipher = rc4.encrypt(plain, key)
        print(cipher)
        open("dump/output", "wb").write(cipher)
        return render_template("rc4.html", file_encrypt=True)
    return 

@app.route('/rc4/file_decrypt', methods=["POST"])
def rc4_decrypt_file():
    if request.method == 'POST':
        key = request.form.get("key")
        f = request.files['file']
        f.save("dump/input")
        f = open(f"dump/input", "rb")
        plain = f.read()
        cipher = rc4.encrypt(plain, key)
        print(cipher)
        open("dump/output", "wb").write(cipher)
        return render_template("rc4.html", file_decrypt=True)
    return 

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(current_app.root_path + "/" + app.config["UPLOAD_FOLDER"])
    if (filename != "output"):
        ext = filename.rsplit('.', 1)[1].lower()
    else :
        ext = 'any' # dummy
    print(ext)
    if(ext in ALLOWED_EXTENSIONS_CITRA):
        return send_file(os.path.join(path,filename), as_attachment=True, mimetype='image/'+str(ext))
    elif(ext in ALLOWED_EXTENSIONS_VIDEO):
        return send_file(os.path.join(path,filename), as_attachment=True, mimetype='video/'+str(ext))
    else:
        return send_file(os.path.join(path,filename), as_attachment=True)

#----------------Steganography------------------
@app.route('/stegano')
def stegano_page():
    return render_template("stegano.html")

@app.route('/stegano/enkripsi')
def stego_enkripsi_page():
    return render_template("stego_enc.html")

def allowed_file(filename):
    if('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CITRA):
        return "gambar"
    elif('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_VIDEO):
	    return "video"
    else:
        return "null" 

@app.route('/stegano/enkripsi', methods=["POST"])
def citra_encrypt():
    if request.method == 'POST':
        respons = ''
        key = request.form.get("key")
        pesan = request.form.get("pesan")
        tipe = request.form.get("tipe_enc")
        sebaran = request.form.get("sebaran")
        f = request.files['file']
        if (f and allowed_file(f.filename)=="gambar"):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            if(sebaran == "acak"):
                if(key != ''):
                    if(tipe == "tanpaenkripsi"):
                        respons = acakgambar.encrypt(os.path.join(app.config["UPLOAD_FOLDER"] ,filename), 
                                            pesan, 
                                            key, 
                                            os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                        status = True
                    elif(tipe == "denganenkripsi"):
                        pesan_rc4 = rc4.encrypt_text(pesan, key)
                        respons = acakgambar.encrypt(os.path.join(app.config["UPLOAD_FOLDER"],filename), 
                                            pesan_rc4, 
                                            key, 
                                            os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                        status = True
                else:
                    flash("Masukkan kunci terlebih dahulu!")
                    status = False
            elif(sebaran == "sekuensial"):
                if(tipe == "tanpaenkripsi"):
                    respons = acak_gambar_seq.encrypt(os.path.join(app.config["UPLOAD_FOLDER"] ,filename), 
                                        pesan, 
                                        os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                    status = True
                elif(tipe == "denganenkripsi"):
                    if(key != ''):
                        pesan_rc4 = rc4.encrypt_text(pesan, key)
                        respons = acak_gambar_seq.encrypt(os.path.join(app.config["UPLOAD_FOLDER"],filename), 
                                            pesan_rc4,  
                                            os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                        status = True
                    else:
                        flash("Masukkan kunci terlebih dahulu!")
                        status = False
            #print('upload_image filename: ' + filename)
            #flash('Gambar berhasil diupload')
        elif(f and (allowed_file(f.filename)=="video")):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            if(sebaran == "acak"):
                if(tipe == "tanpaenkripsi"):
                    responnya = acakvideo.encrypt_driver(app.config["UPLOAD_FOLDER"],
                                        filename, 
                                        pesan, 
                                        key, 
                                        os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                elif(tipe == "denganenkripsi"):
                    pesan_rc4 = rc4.encrypt_text(pesan, key)
                    responnya = acakvideo.encrypt_driver(app.config["UPLOAD_FOLDER"],
                                        filename,
                                        pesan_rc4, 
                                        key, 
                                        os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                if (responnya == -1):
                    flash("Maaf! File tidak ada")
                    status = False
                elif (responnya == -2):
                    flash("Cek jumlah panjang pesan, video tidak cukup!")
                    status = False
                else:
                    respons = responnya
                    status = True
            elif(sebaran == "sekuensial"):
                if(tipe == "tanpaenkripsi"):
                    responnya = acak_video_seq.encrypt_driver(app.config["UPLOAD_FOLDER"],
                                        filename, 
                                        pesan,
                                        os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                elif(tipe == "denganenkripsi"):
                    pesan_rc4 = rc4.encrypt_text(pesan, key)
                    responnya = acak_video_seq.encrypt_driver(app.config["UPLOAD_FOLDER"],
                                        filename,
                                        pesan_rc4, 
                                        os.path.join(app.config["UPLOAD_FOLDER"],"enc-"+filename))
                if (responnya == -1):
                    flash("Maaf! File tidak ada")
                    status = False
                elif (responnya == -2):
                    flash("Cek jumlah panjang pesan, video tidak cukup!")
                    status = False
                else:
                    respons = responnya
                    status = True
        return render_template('stego_enc.html', filename="enc-"+filename, respons=respons, encrypt=status)

@app.route('/stegano/dekripsi')
def stego_dekripsi_page():
    return render_template("stego_dec.html")

@app.route('/stegano/dekripsi', methods=["POST"])
def citra_decrypt():
    jawaban = ''
    if request.method == 'POST':
        key = request.form.get("key")
        tipe = request.form.get("tipe_enc")
        f = request.files['file']
        if f and (allowed_file(f.filename)=="gambar"):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            if(tipe == "tanpadekripsi"):
                jawaban = acakgambar.decrypt(os.path.join(app.config["UPLOAD_FOLDER"],filename), key)
                status = True
            elif(tipe == "dengandekripsi"):
                if(key != ''):
                    ciphernya = acakgambar.decrypt(os.path.join(app.config["UPLOAD_FOLDER"],filename), key)
                    jawaban = rc4.decrypt_text(ciphernya, key)
                    status = True
                else:
                    flash("Masukkan kunci terlebih dahulu!")
                    status = False
        elif(f and (allowed_file(f.filename)=="video")):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            if(tipe == "tanpadekripsi"):
                jawaban = acakvideo.decrypt_driver(app.config["UPLOAD_FOLDER"] ,
                                    filename, 
                                    key)
                if (jawaban == -1):
                    flash("File Video gagal ditemukan!")
                    status = False
                else:
                    status = True
            elif(tipe == "dengandekripsi"):
                ciphernya = acakvideo.decrypt_driver(app.config["UPLOAD_FOLDER"],
                                    filename, 
                                    key)
                if (ciphernya == -1):
                    flash("File Video gagal ditemukan!")
                    status = False
                else:
                    jawaban = rc4.decrypt_text(ciphernya, key)
                    status = True
        return render_template('stego_dec.html', filename=filename, jawaban=jawaban , decrypt=status)

if __name__ == "__main__":
    app.run(debug=True)