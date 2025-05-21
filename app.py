from flask import Flask, request, redirect, jsonify
import string, random

app = Flask(__name__)

# Bellekte basit bir veritabanı gibi
db = {}

# Rastgele kısa kod oluşturma
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# URL kısaltma endpoint'i http://localhost:5000/shorten
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')
    
    if not original_url:
        return jsonify({'error': 'URL eksik'}), 400

    short_code = generate_short_code()
    db[short_code] = original_url

    return jsonify({'short_url': f'http://localhost:5000/{short_code}'})

# Kısaltılmış URL'ye tıklanınca yönlendirme
@app.route('/<short_code>')
def redirect_url(short_code):
    original_url = db.get(short_code)
    if original_url:
        return redirect(original_url)
    return jsonify({'error': 'URL bulunamadı'}), 404

if __name__ == '__main__':
    app.run(debug=True)