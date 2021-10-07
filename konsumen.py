from flask import Flask, request, abort, make_response, jsonify, json
import datetime,jwt
from flask.wrappers import Response
from flask_mysqldb import MySQL
from functools import wraps
app = Flask(__name__)



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'absensi'
mysql = MySQL(app)

@app.route('/input', methods=['POST'])
def input():

        details = request.get_json()
        nama = details['nama']
        tanggal_lahir = details['tanggal_lahir']
        tempat_tinggal = details['tempat_tinggal']
        jabatan = details['jabatan']
        id = details['id']
        password = details['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO karyawan(nama, tanggal_lahir, tempat_tinggal, jabatan, id, password) VALUES (%s, %s, %s, %s, %s, %s)", (nama, tanggal_lahir, tempat_tinggal, jabatan, id, password))
        mysql.connection.commit()
        cur.close()
        return make_response(jsonify(message = "sukses"), 200)
    

@app.route('/update/<int:id>', methods = ['POST'])
def ubah(id):
    cur = mysql.connection.cursor()
    details = request.get_json()
    nama = details['nama']
    tanggal_lahir = details['tanggal_lahir']
    tempat_tinggal = details['tempat_tinggal']
    jabatan = details['jabatan']
    cur.execute("""
       UPDATE karyawan
       SET nama=%s, tanggal_lahir=%s, tempat_tinggal=%s, jabatan=%s
       WHERE id=%s
    """, (nama, tanggal_lahir, tempat_tinggal, jabatan, id))

    mysql.connection.commit()

    return make_response(jsonify(message = "sukses update data"), 200)

@app.route('/delete/<int:id>', methods = ['GET'])
def delete(id):
    cur = mysql.connection.cursor()
    deletedata = "DELETE FROM karyawan WHERE id='%s'"%(id)
    cur.execute(deletedata)

    mysql.connection.commit()
    return make_response(jsonify(message = "sukses delete data"), 200)


app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #http://127.0.0.1:5000/route?token=asdboin2i3oi2

        if not token:
            return json({'message' : 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is Invalid!'}), 403
        
        return f(*args, **kwargs)

    return decorated

@app.route('/register/<int:id>', methods = ['POST'])
def password():
    cur = mysql.connection.cursor()
    details = request.get_json()
    nama = details['nama']
    password = details['password']
    cur.execute("""
       UPDATE karyawan
       SET nama=%s, password =%s
       WHERE id=%s
    """, (nama, password, id))

    mysql.connection.commit()

    return make_response(jsonify(message = "berhasil registrasi"), 200)


@app.route('/protected', methods = ['POST'])
@token_required
def list():
   cur = mysql.connection.cursor()
   cur.execute('''SELECT * FROM karyawan''')
   row_headers=[x[0] for x in cur.description] #this will extract row headers
   rv = cur.fetchall()
   json_data=[]
   for result in rv:
        json_data.append(dict(zip(row_headers,result)))
   return json.dumps(json_data)

@app.route('/login', methods = ['POST'])
def login():
    auth = request.authorization
    cur = mysql.connection.cursor()
    details = request.get_json()
    nama = details['nama']
    password = details['password']
    cur.execute('''SELECT * FROM karyawan WHERE nama ='"+nama+" AND password ='"+password+"''')


    if auth.username == nama and auth.password == password:
        token = jwt.encode({'user' : auth.username, 'exp' :datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token})

    return make_response('Invalid',401,{ 'WWW-Authenticate' : 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run(debug=True)