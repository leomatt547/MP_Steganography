from flask import *
from backend import elgamal_image, elgamal_video, elgamal_audio
import os
import glob
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
ALLOWED_EXTENSIONS_CITRA = set(['png', 'bmp'])
ALLOWED_EXTENSIONS_VIDEO = set(['avi'])
ALLOWED_EXTENSIONS_AUDIO = set(['wav'])
app.config["UPLOAD_FOLDER"]="dump"

def clear_folder():
    files = glob.glob('dump/*')
    files1 = glob.glob('dump/temp/*')
    files2 = glob.glob('dump/temp2/*')
    for f in files:
        try:
            os.remove(f)
        except:
            try:
                for f in files1:
                    os.remove(f)
            except:
                try:
                    for f in files2:
                        os.remove(f)
                except:
                    print("File kosong")

def allowed_file(filename):
    if('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CITRA):
        return "gambar"
    elif('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_VIDEO):
        return "video"
    elif('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_AUDIO):
        return "audio"
    else:
        return "null" 

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

@app.route('/')
def home():
    clear_folder()
    return render_template("index.html")

#---------------------------------STEGO IMAGE--------------------------------------------
@app.route('/image/enkripsi')
def image_enkripsi():
    clear_folder()
    return render_template("image_enkripsi.html")

@app.route('/image/enkripsi', methods=["POST"])
def image_enkripsi_post():
    if (request.method == 'POST'):
        plain = str(request.form.get("plain"))
        f = request.files['stego-file']
        if (f and allowed_file(f.filename)=="gambar"):
            angka_k = int(request.form.get("angka_k"))
            angka_g = int(request.form.get("angka_g"))
            angka_y = int(request.form.get("angka_y"))
            angka_p = int(request.form.get("angka_p"))
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            response = elgamal_image.enkripsi(plain, angka_k, angka_g, angka_y, angka_p, filename)
            print("responsenya",response)
            if(response == -1 or (angka_k < 0) or (angka_k >= angka_p)):
                hasil = "Maaf, pilih angka k yang lain di antara 0 hingga "+ str(angka_p)
                return render_template("image_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)
            else:
                return render_template("image_enkripsi.html",\
                    encrypt=True
                    , filename = str("enc-"+filename)\
                    , hasil = response)
        else:
            hasil = "Maaf, pilih stego file yang lain"
            return render_template("image_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)

@app.route('/image/dekripsi')
def image_dekripsi():
    clear_folder()
    return render_template("image_dekripsi.html")

@app.route('/image/dekripsi', methods=["POST"])
def image_dekripsi_post():
    if (request.method == 'POST'):
        f = request.files['cipher-file']
        if (f and allowed_file(f.filename)=="gambar"):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            angka_x = int(request.form.get("angka_x"))
            angka_p = int(request.form.get("angka_p"))
            response = elgamal_image.dekripsi(os.path.join(app.config["UPLOAD_FOLDER"] ,filename), angka_x, angka_p)
            print(response)
            return render_template("image_dekripsi.html",\
                    encrypt=True\
                    , hasil=response)
        else:
            return render_template("image_dekripsi.html",\
                    encrypt=False\
                    , hasil = "Maaf, masukkan stego bertipe gambar dengan format yang valid")

@app.route('/image/genKey')
def image_genKey():
    clear_folder()
    return render_template("image_key.html")

@app.route('/image/genKey', methods=["POST"])
def image_genKey_post():
    if (request.method == 'POST'):
        angka_p = int(request.form.get("angka_p"))
        angka_g = int(request.form.get("angka_g"))
        angka_x = int(request.form.get("angka_x"))
        response = elgamal_image.getKunci(angka_p, angka_g, angka_x)
        print(len(response))
        if(len(response)==4):
            return render_template("image_key.html", \
                encrypt=True, \
                kunci_public=str(str(response[0])+" "+str(response[1])+" "+str(response[3])),\
                kunci_private=str(str(response[2])+" "+str(response[3])))
        else:
            return render_template("image_key.html", encrypt=False, \
                hasil=response)

#---------------------------------STEGO video--------------------------------------------
@app.route('/video/enkripsi')
def video_enkripsi():
    clear_folder()
    return render_template("video_enkripsi.html")

@app.route('/video/enkripsi', methods=["POST"])
def video_enkripsi_post():
    if (request.method == 'POST'):
        plain = str(request.form.get("plain"))
        f = request.files['stego-file']
        if (f and allowed_file(f.filename)=="video"):
            angka_k = int(request.form.get("angka_k"))
            angka_g = int(request.form.get("angka_g"))
            angka_y = int(request.form.get("angka_y"))
            angka_p = int(request.form.get("angka_p"))
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            response = elgamal_video.enkripsi(plain, angka_k, angka_g, angka_y, angka_p, filename)
            print("responsenya",response)
            if(response == -1 or (angka_k < 0) or (angka_k >= angka_p)):
                hasil = "Maaf, pilih angka k yang lain di antara 0 hingga "+ str(angka_p)
                return render_template("video_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)
            else:
                return render_template("video_enkripsi.html",\
                    encrypt=True
                    , filename = str("enc-"+filename)\
                    , hasil = response)
        else:
            hasil = "Maaf, pilih stego file yang lain"
            return render_template("video_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)

@app.route('/video/dekripsi')
def video_dekripsi():
    clear_folder()
    return render_template("video_dekripsi.html")

@app.route('/video/dekripsi', methods=["POST"])
def video_dekripsi_post():
    if (request.method == 'POST'):
        f = request.files['cipher-file']
        if (f and allowed_file(f.filename)=="video"):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            angka_x = int(request.form.get("angka_x"))
            angka_p = int(request.form.get("angka_p"))
            response = elgamal_video.dekripsi(filename, angka_x, angka_p)
            print(response)
            return render_template("video_dekripsi.html",\
                    encrypt=True\
                    , hasil=response)
        else:
            return render_template("video_dekripsi.html",\
                    encrypt=False\
                    , hasil = "Maaf, masukkan stego bertipe gambar dengan format yang valid")

@app.route('/video/genKey')
def video_genKey():
    clear_folder()
    return render_template("video_key.html")

@app.route('/video/genKey', methods=["POST"])
def video_genKey_post():
    if (request.method == 'POST'):
        angka_p = int(request.form.get("angka_p"))
        angka_g = int(request.form.get("angka_g"))
        angka_x = int(request.form.get("angka_x"))
        response = elgamal_image.getKunci(angka_p, angka_g, angka_x)
        print(len(response))
        if(len(response)==4):
            return render_template("video_key.html", \
                encrypt=True, \
                kunci_public=str(str(response[0])+" "+str(response[1])+" "+str(response[3])),\
                kunci_private=str(str(response[2])+" "+str(response[3])))
        else:
            return render_template("video_key.html", encrypt=False, \
                hasil=response)

#---------------------------------STEGO AUDIO--------------------------------------------
@app.route('/audio/enkripsi')
def audio_enkripsi():
    clear_folder()
    return render_template("audio_enkripsi.html")

@app.route('/audio/enkripsi', methods=["POST"])
def audio_enkripsi_post():
    if (request.method == 'POST'):
        plain = str(request.form.get("plain"))
        f = request.files['stego-file']
        if (f and allowed_file(f.filename)=="audio"):
            angka_k = int(request.form.get("angka_k"))
            angka_g = int(request.form.get("angka_g"))
            angka_y = int(request.form.get("angka_y"))
            angka_p = int(request.form.get("angka_p"))
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            response = elgamal_audio.enkripsi(plain, angka_k, angka_g, angka_y, angka_p, filename)
            print("responsenya",response)
            if(response == -1 or (angka_k < 0) or (angka_k >= angka_p)):
                hasil = "Maaf, pilih angka k yang lain di antara 0 hingga "+ str(angka_p)
                return render_template("audio_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)
            else:
                return render_template("audio_enkripsi.html",\
                    encrypt=True
                    , filename = str("enc-"+filename)\
                    , hasil = response)
        else:
            hasil = "Maaf, pilih stego file yang lain"
            return render_template("audio_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)

@app.route('/audio/dekripsi')
def audio_dekripsi():
    clear_folder()
    return render_template("audio_dekripsi.html")

@app.route('/audio/dekripsi', methods=["POST"])
def audio_dekripsi_post():
    if (request.method == 'POST'):
        f = request.files['cipher-file']
        if (f and allowed_file(f.filename)=="audio"):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            angka_x = int(request.form.get("angka_x"))
            angka_p = int(request.form.get("angka_p"))
            response = elgamal_audio.dekripsi(os.path.join(app.config["UPLOAD_FOLDER"] ,filename), angka_x, angka_p)
            print(response)
            return render_template("audio_dekripsi.html",\
                    encrypt=True\
                    , hasil=response)
        else:
            return render_template("audio_dekripsi.html",\
                    encrypt=False\
                    , hasil = "Maaf, masukkan stego bertipe gambar dengan format yang valid")

@app.route('/audio/genKey')
def audio_genKey():
    clear_folder()
    return render_template("audio_key.html")

@app.route('/audio/genKey', methods=["POST"])
def audio_genKey_post():
    if (request.method == 'POST'):
        angka_p = int(request.form.get("angka_p"))
        angka_g = int(request.form.get("angka_g"))
        angka_x = int(request.form.get("angka_x"))
        response = elgamal_image.getKunci(angka_p, angka_g, angka_x)
        print(len(response))
        if(len(response)==4):
            return render_template("audio_key.html", \
                encrypt=True, \
                kunci_public=str(str(response[0])+" "+str(response[1])+" "+str(response[3])),\
                kunci_private=str(str(response[2])+" "+str(response[3])))
        else:
            return render_template("audio_key.html", encrypt=False, \
                hasil=response)



if __name__ == "__main__":
    app.run(debug=True)