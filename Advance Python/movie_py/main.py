from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

URL_movie_search = "https://api.themoviedb.org/3/search/movie"
param = {'api_key': '5559462b5f37070567f7964b20779ee7', 'language': 'en-US', 'include_adult': 'true', 'query': ''}

movie_param = {'api_key': '5559462b5f37070567f7964b20779ee7'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_list.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db = SQLAlchemy(app)


class movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(60), nullable=False)
    img_url = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.book_name


db.create_all()


def data_transfer_sql(t, y, d, r, rk, re, img):
    movie_det = movie(title=t, year=y, desc=d, rating=r, ranking=rk, review=re, img_url=img)
    db.session.add(movie_det)
    db.session.commit()


class edit_form(FlaskForm):
    ratings = StringField(u'Your Rating out 10', validators=[DataRequired()])
    review = StringField(u'Your Review', validators=[DataRequired()])
    submit = SubmitField('submit')


class add_movie(FlaskForm):
    movie_search = StringField(validators=[DataRequired()])
    add = SubmitField('Add Movie')


@app.route('/<mov_id>', methods=['POST', 'GET'])
def update(mov_id):
    form = edit_form()
    mov = movie.query.get(mov_id)
    if form.validate_on_submit():
        mov.rating = float(form.ratings.data)
        mov.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=mov, form=form)


@app.route('/delete/<mov_id>', methods=['POST', 'GET'])
def delete(mov_id):
    mov = movie.query.get(mov_id)
    db.session.delete(mov)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/")
def home():
    all_movies_list = movie.query.order_by(movie.rating).all()
    j = 1
    for i in all_movies_list:
        i.ranking = j
        j = 1 + j
    db.session.commit()
    return render_template("index.html", ml=all_movies_list)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = add_movie()
    if form.validate_on_submit():
        mov_name = form.movie_search.data
        param['query'] = mov_name
        response = requests.get(url=URL_movie_search, params=param)
        movie_list = response.json()
        movie_list = movie_list['results']
        return render_template('select.html', movies_list=movie_list)

    return render_template('add.html', form=form)


@app.route('/new_add/<ID>', methods=['POST', "GET"])
def add_new_details(ID):
    form = edit_form()
    URL_movie_details = f"https://api.themoviedb.org/3/movie/{ID}"
    response = requests.get(url=URL_movie_details, params=movie_param)
    mov = response.json()
    if form.validate_on_submit():
        rating = float(form.ratings.data)
        review = form.review.data
        img = f'https://image.tmdb.org/t/p/original/{mov["poster_path"]}'
        data_transfer_sql(mov['original_title'], mov['release_date'], mov['overview'], rating, 0, review, img)
        return redirect(url_for('home'))
    return render_template('edit.html', movie_name=mov['original_title'], form=form)


if __name__ == '__main__':
    app.run(debug=True)
