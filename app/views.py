import psycopg2
from psycopg2.extras import RealDictCursor
from flask import render_template, flash, redirect, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from json import dumps
from slugify import slugify
from app import app, db, lm
from .forms import NewsForm, LoginForm
from .models import User

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

######### PUBLIC ROUTES

@app.route('/')
@app.route('/index')
def index():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM news LIMIT 2""")
    news = cur.fetchall()
    cur.close()
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM countries ORDER BY name""")
    countries = cur.fetchall()
    cur.close()
    
    return render_template("index.html",
                           title='Home',
                           countries=countries,
                           news=news)

@app.route('/countries/<country_slug>')
def country(country_slug):
    conn = psycopg2.connect(app.config['CONN_STRING'])
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM countries ORDER BY name""")
    countries = cur.fetchall()
    cur.close()
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM countries WHERE slug=%s",[country_slug])
    country = cur.fetchone()
    cur.close()
    
    return render_template("country.html",
                           title='Country',
                           countries=countries,
                           country=country)

@app.route('/tool')
def tool():
    return render_template('tool.html')

@app.route('/news')
def news():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM news""")
    news = cur.fetchall()
    cur.close()
    return render_template('news.html',news=news)

@app.route('/news/<item_id>')
def news_item(item_id):
    conn = psycopg2.connect(app.config['CONN_STRING'])
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM news WHERE id=%s",[item_id])
    item = cur.fetchone()
    cur.close()
    return render_template('news_item.html',item=item)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/datasets_codebooks')
def datasets_codebooks():
    return render_template('datasets_codebooks.html')


######### ADMIN ROUTES
 
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
        login_user(User.query.get(1))
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("admin_news"))
    return render_template("admin/login.html", form=form) 

                    
@app.route('/admin/news', methods=['GET', 'POST'])
@login_required
def admin_news():
    form = NewsForm()
    if form.validate_on_submit():
    	flash('News item "%s" created' %
              (form.title.data))
        conn = psycopg2.connect(app.config['CONN_STRING'])
        cur = conn.cursor()
        cur.execute("INSERT INTO news (title, content, slug) VALUES (%s, %s, %s)",(form.title.data,form.content.data,slugify(form.title.data)))
        conn.commit()
        cur.close()
        return redirect('/news')
    return render_template('admin/news-item.html', 
                           title='News',
                           form=form)

@app.route("/admin/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
                           

######### API ROUTES

@app.route('/api/countries')
def api_countries():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM countries ORDER BY name""")
    return dumps(cur.fetchall())

@app.route('/api/categories')
def api_categories():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM categories ORDER BY name""")
    return dumps(cur.fetchall())

@app.route('/api/topics')
def api_topics():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT CONCAT(TRIM(to_char(m.majortopic,'999')),'_',m.shortname) as topic, array_agg(CONCAT(TRIM(to_char(t.id,'9999')),'_',t.shortdescription)) as subtopics FROM major_topics m JOIN topics t ON m.MajorTopic = t.MajorTopic GROUP by m.SHORTNAME,m.majortopic ORDER BY m.SHORTNAME""")
    return dumps(cur.fetchall())

@app.route('/api/datasets')
def api_datasets():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT category, short_display as name FROM datasets WHERE controller IS NOT NULL ORDER BY short_display""")
    return dumps(cur.fetchall())
    
@app.route('/api/subtopic/<subtopic>')
def api(subtopic):
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT year::integer, count(keyid) AS CNT FROM congressional_hearings WHERE capsubtopic =%s GROUP BY year ORDER by year",[subtopic])
    d = cur.fetchall()
    data = []
    for i in range(2001,2011):
        found = False
        for r in d:
            if (r["year"] == i):
                data.append(r["cnt"])
                found = True
        if (found == False):
            data.append(0)
    return dumps(data)