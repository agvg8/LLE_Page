from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import os



app = Flask(__name__)
app.secret_key = 'tajny_klucz'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'portfolio.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class PortfolioEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.String(10))
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(100))

#baza danych
messages = []

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

@app.route("/")
def home():
    return render_template("index.html", active_page="home")

@app.route("/onas")
def onas():
    return render_template("onas.html", active_page="onas")


@app.route('/portfolio')
def portfolio():
    selected_make = request.args.get('make')

    # unikalne marki do listy rozwijanej
    makes = db.session.query(PortfolioEntry.make).distinct().all()
    makes = [make[0] for make in makes]  # lista stringów

    if selected_make:
        entries = PortfolioEntry.query.filter_by(make=selected_make).all()
    else:
        entries = PortfolioEntry.query.all()

    return render_template(
        'portfolio.html',
        entries=entries,
        makes=makes,
        selected_make=selected_make,
        active_page='portfolio'
    )

@app.route('/kontakt', methods=['GET', 'POST'])
def kontakt():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages.append(data)  # dodajemy do naszej listy
        flash('Wiadomość wysłana!', 'success')
        return redirect(url_for('kontakt'))
    return render_template('kontakt.html')

@app.route('/LLEAdmin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('login.html', error="Niepoprawny login lub hasło.")
    return render_template('login.html')

@app.route('/LLEAdmin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/LLEAdmin')
@admin_required
def admin_panel():
    return render_template('admin_panel.html', messages=messages)

@app.route('/LLEAdmin/kontakt_manager')
@admin_required
def kontakt_manager():
    return render_template('kontakt_manager.html', messages=messages, active_page='kontakt_menager')

@app.route('/LLEAdmin/kontakt_manager/delete/<int:msg_id>', methods=['POST'])
@admin_required
def delete_message(msg_id):
    if 0 <= msg_id < len(messages):
        messages.pop(msg_id)
        flash('Zapytanie zostało usunięte.', 'success')
    else:
        flash('Nie znaleziono zapytania.', 'danger')
    return redirect(url_for('kontakt_manager'))

@app.route('/LLEAdmin/portfolio_manager', methods=['GET', 'POST'])
def portfolio_manager():
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        description = request.form['description']
        file = request.files['image']

        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_entry = PortfolioEntry(make=make, model=model, year=year, description=description, image_filename=filename)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('portfolio_manager'))

    entries = PortfolioEntry.query.all()
    return render_template('portfolio_manager.html', entries=entries, active_page='portfolio_menager')

@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry = PortfolioEntry.query.get_or_404(entry_id)

    # Usuń plik obrazka
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], entry.image_filename)
    if os.path.exists(image_path):
        os.remove(image_path)

    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('portfolio_manager'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
