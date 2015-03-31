import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import render_template, flash, redirect, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
from json import dumps
from slugify import slugify
from app import app, db, lm, newsimages, countryimages, researchimages
from .models import User, News, Country, Research, Staff
from .forms import NewsForm, LoginForm, CountryForm, UserForm, ResearchForm

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

######### PUBLIC ROUTES

@app.route('/')
@app.route('/index')
def index():
    news = News.query.paginate(1, 2, False).items
    for item in news:
        if item.filename:
            url = newsimages.url(item.filename)
            item.url = url
    countries = Country.query.order_by(Country.name)
    return render_template("index.html",
                           title='Home',
                           countries=countries,
                           news=news)

@app.route('/countries/<country_slug>')
def country(country_slug):
    countries = Country.query.order_by(Country.name)
    country = Country.query.filter_by(slug=country_slug).first()
    url = countryimages.url(country.filename) if country.filename else None
    return render_template("country.html",
                           title='Country',
                           countries=countries,
                           url = url,
                           country=country)

@app.route('/tool')
def tool():
    return render_template('tool.html')

@app.route('/news')
@app.route('/news/<int:page>')
def news(page=1):
    news = News.query.paginate(page, 3, False)
    for item in news.items:
        if item.filename:
            url = newsimages.url(item.filename)
            item.url = url
    return render_template('news.html',news=news)

@app.route('/news/<news_slug>')
def news_item(news_slug):    
    item = News.query.filter_by(slug=news_slug).first()
    if item.filename:
            url = newsimages.url(item.filename)
            item.url = url
    news = News.query.filter(News.slug!=news_slug).limit(2).all()
    return render_template('news_item.html',item=item,news=news)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/datasets_codebooks')
def datasets_codebooks():
    return render_template('datasets_codebooks.html')


######### ADMIN ROUTES


## LOGIN / LOGOUT / LANDING

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).filter_by(password=form.password.data).first()
        if user is not None:
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('admin_countries_slug',slug=user.country.slug) if user.country else request.args.get("next"))
        else:
            flash("Login credentials incorrect!")
            return redirect(url_for("login"))
    return render_template("admin/login.html", form=form) 

@app.route("/admin/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))
 
 
@app.route("/admin")
@login_required
def landing():
    return render_template("admin/index.html")
 
## NEWS

@app.route('/admin/news')
@login_required
def admin_news_list():
    news = News.query.all()
    return render_template('admin/news_list.html', 
                           title='News',
                           news=news)
                    
@app.route('/admin/news/<slug>', methods=['GET', 'POST'])
@login_required
def admin_news_slug(slug):
    news = News() if slug == 'add' else News.query.filter_by(slug=slug).first()
    form = NewsForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = newsimages.save(request.files['image'])
            news.filename = filename
        news.title = form.title.data
        news.content = form.content.data
        news.slug = slugify(news.title)
        if slug == 'add':
            db.session.add(news)
        db.session.commit()
    	flash('News item "%s" saved' %
              (form.title.data))
        return redirect('admin/news')
    else:
        url = newsimages.url(news.filename) if news.filename else None
        form.title.data = news.title
        form.content.data = news.content
    
    return render_template('admin/news_item.html', 
                           id=news.id,
                           url=url,
                           form=form)

@app.route('/admin/news/delete/<id>')
@login_required
def admin_news_delete(id):
    news = News.query.filter_by(id=id).first()
    if news is not None:
        title = news.title
        db.session.delete(news)
        db.session.commit()
        flash('News item "%s" deleted' %
              (title))
        return redirect('admin/news')
    return redirect('index')

@app.route('/admin/news/removeimage/<id>')
@login_required
def admin_news_removeimage(id):
    news = News.query.filter_by(id=id).first()
    if news is not None:
        #if os.path.isfile('/var/www/cap/app/static/img/news/' + news.filename):
        #    os.remove('/var/www/cap/app/static/img/news/' + news.filename)
        news.filename = None
        db.session.commit()
        return redirect('admin/news/' + news.slug)
    return redirect('index')
       

## COUNTRIES

@app.route('/admin/countries')
@login_required
def admin_countries():
    countries = Country.query.order_by(Country.name)
    return render_template('admin/country_list.html', 
                           title='Country',
                           countries=countries)
                                               
@app.route('/admin/countries/<slug>', methods=['GET', 'POST'])
@login_required
def admin_countries_slug(slug):
    country = Country() if slug == 'add' else Country.query.filter_by(slug=slug).first()
    form = CountryForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = countryimages.save(request.files['image'])
            country.filename = filename
        country.name = form.name.data
        country.principal = form.principal.data
        country.location = form.location.data
        country.heading = form.heading.data
        country.about = form.about.data
        country.slug = slugify(country.name)
        if slug == 'add':
            db.session.add(country)
        db.session.commit()
    	flash('Country "%s" saved' %
              (form.name.data))
        return redirect( url_for('admin_countries_slug',slug=current_user.country.slug) if current_user.country else 'admin/countries' )
    else:
        url = countryimages.url(country.filename) if country.filename else None
        form.name.data = country.name
        form.principal.data = country.principal
        form.location.data = country.location
        form.heading.data = country.heading
        form.about.data = country.about
    
    return render_template('admin/country.html', 
                           id=country.id,
                           slug=country.slug,
                           url=url,
                           form=form)
 

@app.route('/admin/countries/delete/<id>')
@login_required
def admin_countries_delete(id):
    country = Country.query.filter_by(id=id).first()
    if country is not None:
        title = country.name
        db.session.delete(country)
        db.session.commit()
        flash('Country "%s" deleted' %
              (title))
        return redirect('admin/countries')
    return redirect('index')

@app.route('/admin/countries/removeimage/<id>')
@login_required
def admin_countries_removeimage(id):
    country = Country.query.filter_by(id=id).first()
    if country is not None:
        country.filename = None
        db.session.commit()
        return redirect('admin/countries/' + country.slug)
    return redirect('index')                         

## USERS

@app.route('/admin/users')
@login_required
def admin_users():
    users = User.query.all()
    return render_template('admin/user_list.html',
                           users=users)
                                               
@app.route('/admin/users/<id>', methods=['GET', 'POST'])
@login_required
def admin_users_id(id):
    user = User() if id == 'add' else User.query.filter_by(id=id).first()
    form = UserForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.password = form.password.data
        user.country = form.country.data
        if id == 'add':
            db.session.add(user)
        db.session.commit()
    	flash('User "%s" saved' %
              (form.name.data))
        return redirect('admin/users')
    else:
        form.name.data = user.name
        form.email.data = user.email
        form.password.data = user.password
        form.country.data = user.country
    
    return render_template('admin/user.html', 
                           id=user.id,
                           form=form)
                           
@app.route('/admin/users/delete/<id>')
@login_required
def admin_users_delete(id):
    user = User.query.filter_by(id=id).first()
    if user is not None:
        name = user.name
        db.session.delete(user)
        db.session.commit()
        flash('User "%s" deleted' %
              (user.name))
        return redirect('admin/users')
    return redirect('index')


## RESEARCH

@app.route('/admin/countries/<slug>/research', methods=['GET', 'POST'])
@login_required
def admin_countries_research(slug):
    country = Country.query.filter_by(slug=slug).first()
    research = Research.query.filter_by(country_id=country.id).all()
    return render_template('admin/country_research.html', 
                           country=country,
                           research=research)

@app.route('/admin/countries/<slug>/research/<id>', methods=['GET', 'POST'])
@login_required
def admin_countries_research_id(slug,id):
    country = Country.query.filter_by(slug=slug).first()
    app.logger.debug('woah')
    app.logger.debug(country)
    research = Research() if id == 'add' else Research.query.filter_by(id=id).first()
    form = ResearchForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = researchimages.save(request.files['image'])
            research.filename = filename
        research.title = form.title.data
        research.body = form.body.data
        if id == 'add':
            research.country_id = country.id
            db.session.add(research)
        db.session.commit()
    	flash('Research item "%s" saved' %
              (form.title.data))
        return redirect('admin/countries/' + slug + '/research')
    else:
        url = researchimages.url(research.filename) if research.filename else None
        form.title.data = research.title
        form.body.data = research.body
    
    return render_template('admin/country_research_item.html',
                           slug=slug,
                           country=country,
                           id=research.id,
                           url=url,
                           form=form)

@app.route('/admin/countries/<slug>/research/delete/<id>')
@login_required
def admin_research_delete(slug,id):
    research = Research.query.filter_by(id=id).first()
    if research is not None:
        title = research.title
        db.session.delete(research)
        db.session.commit()
        flash('News item "%s" deleted' %
              (title))
        return redirect('admin/countries/' + slug + '/research')
    return redirect('index')

@app.route('/admin/countries/<slug>/research/removeimage/<id>')
@login_required
def admin_research_removeimage(slug,id):
    research = Research.query.filter_by(id=id).first()
    if research is not None:
        #if os.path.isfile('/var/www/cap/app/static/img/news/' + news.filename):
        #    os.remove('/var/www/cap/app/static/img/news/' + news.filename)
        research.filename = None
        db.session.commit()
        return redirect('admin/countries/' + slug + '/research/' + id)
    return redirect('index')


######### API ROUTES

@app.route('/api/countries')
def api_countries():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM country ORDER BY name""")
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
    cur.execute("""SELECT year::integer, count(keyid) AS CNT FROM congressional_hearings WHERE capsubtopic =%s GROUP BY year ORDER by year""",[subtopic])
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