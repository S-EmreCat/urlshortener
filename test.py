from flask import Flask, request

app = Flask(__name__)


"""
postman > body - x-www-form-urlencoded 
Key	    Value
isim	Emre
"""
@app.route('/gonder', methods=['POST'])
def gonder():
    isim = request.form['isim']
    return f'Hoş geldin, {isim}!'

if __name__ == '__main__':
    app.run()