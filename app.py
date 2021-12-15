from flask import *
from backend import elgamal
import os
import glob
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
ALLOWED_EXTENSIONS_CITRA = set(['png', 'bmp'])
#ALLOWED_EXTENSIONS_VIDEO = set(['avi'])
app.config["UPLOAD_FOLDER"]="dump"

def clear_folder():
    files = glob.glob('dump/*')
    for f in files:
        os.remove(f)

def allowed_file(filename):
    if('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CITRA):
        return "gambar"
    elif('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_VIDEO):
        return "video"
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
    # elif(ext in ALLOWED_EXTENSIONS_VIDEO):
    #     return send_file(os.path.join(path,filename), as_attachment=True, mimetype='video/'+str(ext))
    # else:
    #     return send_file(os.path.join(path,filename), as_attachment=True)

@app.route('/')
def home():
    clear_folder()
    return render_template("index.html")

#ElGamal
@app.route('/image/enkripsi')
def elgamal_enkripsi():
    clear_folder()
    return render_template("elgamal_enkripsi.html")

@app.route('/image/enkripsi', methods=["POST"])
def elgamal_enkripsi_post():
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
            response = elgamal.enkripsi(plain, angka_k, angka_g, angka_y, angka_p, filename)
            print("responsenya",response)
            if(response == -1 or (angka_k < 0) or (angka_k >= angka_p)):
                hasil = "Maaf, pilih angka k yang lain di antara 0 hingga "+ str(angka_p)
                return render_template("elgamal_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)
            else:
                return render_template("elgamal_enkripsi.html",\
                    encrypt=True
                    , filename = str("enc-"+filename)\
                    , hasil = response)
        else:
            hasil = "Maaf, pilih stego file yang lain"
            return render_template("elgamal_enkripsi.html",\
                    encrypt=False\
                    , hasil=hasil)


@app.route('/image/dekripsi')
def elgamal_dekripsi():
    clear_folder()
    return render_template("elgamal_dekripsi.html")

@app.route('/image/dekripsi', methods=["POST"])
def elgamal_dekripsi_post():
    if (request.method == 'POST'):
        f = request.files['cipher-file']
        if (f and allowed_file(f.filename)=="gambar"):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"] ,filename))
            angka_x = int(request.form.get("angka_x"))
            angka_p = int(request.form.get("angka_p"))
            response = elgamal.dekripsi(os.path.join(app.config["UPLOAD_FOLDER"] ,filename), angka_x, angka_p)
            print(response)
            return render_template("elgamal_dekripsi.html",\
                    encrypt=True\
                    , hasil=response)
        else:
            return render_template("elgamal_dekripsi.html",\
                    encrypt=False\
                    , hasil = "Maaf, masukkan stego bertipe gambar dengan format yang valid")

@app.route('/image/genKey')
def elgamal_genKey():
    clear_folder()
    return render_template("elgamal_key.html")

@app.route('/image/genKey', methods=["POST"])
def elgamal_genKey_post():
    if (request.method == 'POST'):
        angka_p = int(request.form.get("angka_p"))
        angka_g = int(request.form.get("angka_g"))
        angka_x = int(request.form.get("angka_x"))
        response = elgamal.getKunci(angka_p, angka_g, angka_x)
        print(len(response))
        if(len(response)==4):
            return render_template("elgamal_key.html", \
                encrypt=True, \
                kunci_public=str(str(response[0])+" "+str(response[1])+" "+str(response[3])),\
                kunci_private=str(str(response[2])+" "+str(response[3])))
        else:
            return render_template("elgamal_key.html", encrypt=False, \
                hasil=response)

if __name__ == "__main__":
    app.run(debug=True)