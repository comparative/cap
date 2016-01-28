import shutil
import os
import uuid
import psycopg2
import urllib
import urllib2
import csv
import time
import tinys3
from sqlalchemy import desc
from psycopg2.extras import RealDictCursor
from datetime import datetime
from functools import wraps, update_wrapper
from flask import Response, render_template, flash, redirect, url_for, request, make_response, send_file, abort, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
from json import dump, dumps, loads
from slugify import slugify
from app import app, db, lm, newsimages, countryimages, staffimages, researchfiles, researchimages, adhocfiles, slideimages, codebookfiles, datasetfiles, topicsfiles
from .models import User, News, Country, Research, Staff, Page, File, Slide, Chart, Dataset, Category, Staticdataset
from .forms import NewsForm, LoginForm, CountryForm, UserForm, ResearchForm, StaffForm, PageForm, FileForm, SlideForm, DatasetForm, StaticDatasetForm
from datetime import datetime

s3 = tinys3.Pool(app.config['S3_ACCESS_KEY'],app.config['S3_SECRET_KEY'],app.config['S3_BUCKET'])

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

######## robots.txt

@app.route('/robots.txt')
#@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

######### CATCH ALL

#@app.route('/', defaults={'path': ''})
#@app.route('/<path:path>')
#def catch_all(path):
#    return 'Comparative Agendas is moving to a new server!  Please try again tomorrow.  Thanks for your patience.'

######### CHARTING ROUTES

@app.route('/tooltest')
def tooltest():
    return render_template('tooltest.html')

@app.route('/tool')
@app.route('/tool/<slug>')
def tool(slug=None):
    
    # identify user
    if 'captool_user' in request.cookies:
        user = request.cookies['captool_user']
    else:
        user = str(uuid.uuid1())
        
    # thumbnails for this user?
    recent = Chart.query.filter_by(user=user).order_by(desc(Chart.date)).all()
    
    # were we passed a permalink slug?
    exists = Chart.query.filter_by(slug=slug).first()
    options = exists.options if exists else None
    
    # were we passed a project id?
    projectid = request.args.get('project')
    
    # send response
    resp=make_response(render_template('tool.html',baseUrl=app.config['TOOL_BASE_URL'],exportUrl=app.config['HIGHCHARTS_EXPORT_URL'],user=user,slug=slug,options=options,recent=recent,projectid=projectid))    
    resp.set_cookie('captool_user',value=user)
    return resp

@app.route('/charts/save/<user>/<slug>', methods=['POST'])
def save_chart(user,slug):
    exists = Chart.query.filter_by(slug=slug).first()
    if exists:
        exists.unpinned = False
    else:
        chart = Chart()
        chart.slug = slug
        chart.user = user
        chart.options = request.get_data()
        db.session.add(chart)
    db.session.commit()
    return 'cool',200
    
@app.route('/charts/saveunpinned/<user>/<slug>', methods=['POST'])
def save_chart_unpinned(user,slug):
    exists = Chart.query.filter_by(slug=slug).first()
    if not exists:
        chart = Chart()
        chart.slug = slug
        chart.user = user
        chart.options = request.get_data()
        chart.unpinned = True
        db.session.add(chart)
        db.session.commit()
    return 'cool',200
    
@app.route('/charts/unpin/<slug>', methods=['POST'])
def remove_chart(slug):
    chart = Chart.query.filter_by(slug=slug).first()
    if chart is not None:
        chart.unpinned = True
        db.session.commit()
    return 'cool',200

@app.route('/charts/<slug>')
@app.route('/charts/<slug>.png')
@app.route('/charts/<slug>/<switch>')
def charts(slug,switch=None):
    exists = Chart.query.filter_by(slug=slug).first()
    if exists and switch != "embed":
        url = 'http://104.237.136.8:8080/highcharts-export-web/'
        values = {}
        myoptions = loads(exists.options)
        #myoptions.update({'legend': {'enabled': 'true'}})        
        #app.logger.debug(myoptions)
        values['options'] = dumps(myoptions)
        values['type'] = 'image/png'
        values['width'] = '600'
        values['constr'] = 'Chart'
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        resp = make_response(response.read())
        resp.headers['Content-Type'] = 'image/png'
        if switch == "download":
            resp.headers['Content-Disposition'] = 'attachment; filename=' + slug + '.png'
        return resp
    elif exists and switch == "embed":
        return 'nope'
    else:
        return 'not found',404  

@app.route('/embed/<slug>')
def embed(slug):
    exists = Chart.query.filter_by(slug=slug).first()
    if exists:
        return render_template('embed.html',options=exists.options)
    else:
        return 'not found',404

######### CMS ROUTES

@app.route('/')
def index():
    #slides = Slide.query.filter_by(active=True).paginate(1,3,False).items
    slides = Slide.query.filter_by(active=True).all()
    for item in slides:
        if item.imagename:
            #url = slideimages.url(item.imagename)
            url = app.config['S3_URL'] + 'slideimages/' + item.imagename
            item.url = url
    news = News.query.order_by(desc(News.saved_date)).paginate(1, 3, False).items
    for item in news:
        if item.filename:
            #url = newsimages.url(item.filename)
            #item.url = url
            item.url = app.config['S3_URL'] + 'newsimages/' + item.filename
    countries = Country.query.order_by(Country.name)
    return render_template("index.html",
                           countries=countries,
                           slides=slides,
                           news=news)

@app.route('/news')
@app.route('/news/<int:page>')
def news(page = 1):
    countries = Country.query.order_by(Country.name)
    news = News.query.order_by(desc(News.saved_date)).paginate(page, 3, False)
    for item in news.items:
        if item.filename:
            #url = newsimages.url(item.filename)
            url = app.config['S3_URL'] + 'newsimages/' + item.filename
            item.url = url
    return render_template('news.html',news=news,countries=countries)

@app.route('/news/<slug>')
def news_item(slug):    
    item = News.query.filter_by(slug=slug).first()
    if item.filename:
            #url = newsimages.url(item.filename)
            url = app.config['S3_URL'] + 'newsimages/' + item.filename
            item.url = url
    news = News.query.filter(News.slug!=slug).order_by(desc(News.saved_date)).limit(3).all()
    return render_template('news_item.html',item=item,news=news)

@app.route('/about')
def about():
    return render_template('about.html')

# ALL OF EM
@app.route('/datasets_codebooks')
def datasets_codebooks():
    intro = Page.query.filter_by(slug='datasets-intro').first()
    countries = Country.query.order_by(Country.name)
    categories = Category.query.all()
    cats = []
    cur = db.session.connection().connection.cursor()
    for category in categories:
        countries_for_category = []
        sql = """
        SELECT DISTINCT country.id AS id, country.name AS name FROM dataset INNER JOIN country on dataset.country_id = country.id WHERE dataset.category_id = %s AND dataset.ready=True ORDER BY country.name    
        """
        cur.execute(sql,[category.id])
        for item in cur.fetchall():
            
            c = {}
            
            # get datasets for this country in this category     
            datasets = []
            for u in Dataset.query.filter_by(category_id=category.id).filter_by(country_id=item[0]).filter_by(ready=True).order_by('display').all():
                datasets.append(u.__dict__)
            for u in Staticdataset.query.filter_by(category_id=category.id).filter_by(country_id=item[0]).order_by('display').all():
                datasets.append(u.__dict__)
            
            datasets = sorted(datasets, key=lambda k: k['display']) 
            
            
            c['name'] = item[1]
            c['datasets'] = datasets

            countries_for_category.append(c)
            
        if len(countries_for_category) > 0:
            setattr(category, 'countries', countries_for_category)
            cats.append(category)
        
        
        
            
    return render_template("datasets_codebooks.html",intro=intro,categories=cats,countries=countries)

@app.route('/codebook')
def cap_codebook():
    countries = Country.query.order_by(Country.name)
    return render_template('codebook.html',countries=countries)  

@app.route('/pages/<slug>')
def page(slug):
    countries = Country.query.order_by(Country.name)
    page = Page.query.filter_by(slug=slug).first()
    return render_template('page.html',page=page,countries=countries)

@app.route('/files/<slug>')
#@nocache
def file(slug):
    file = File.query.filter_by(slug=slug).first()
    if file:
        if file.filename:
            path = adhocfiles.path(file.filename)
            return send_file(path)
    else:
        abort(404)

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
            return redirect(request.args.get("next") or url_for("admin"))
            #return redirect(url_for('admin_country_item',slug=user.country.slug) if user.country else request.args.get("next"))
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
def admin():
    return redirect(url_for('admin_country_item',slug=current_user.country.slug)) if current_user.country else render_template("admin/index.html")
 
## PAGES

@app.route('/admin/pages')
@login_required
def admin_page_list():
    pages = Page.query.order_by(Page.title)
    return render_template('admin/page_list.html',
                           pages=pages)
                                               
@app.route('/admin/pages/<slug>', methods=['GET', 'POST'])
@login_required
def admin_page_item(slug):
    page = Page() if slug == 'add' else Page.query.filter_by(slug=slug).first()
    form = PageForm()
    if form.validate_on_submit():
        page.title = form.title.data
        page.body = form.body.data
        if slug == 'add':
            page.slug = slugify(page.title,to_lower=True)
            db.session.add(page)
        db.session.commit()
    	flash('Page "%s" saved' %
              (form.title.data))
        return redirect(url_for('admin_page_list'))
    else:
        if request.method == 'GET':
            form.title.data = page.title
            form.body.data = page.body
    
    return render_template('admin/page_item.html', 
                           id=page.id,
                           slug=page.slug,
                           form=form)
 

@app.route('/admin/pages/delete/<id>')
@login_required
def admin_page_delete(id):
    page = Page.query.filter_by(id=id).first()
    if page is not None:
        title = page.title
        db.session.delete(page)
        db.session.commit()
        flash('Page "%s" deleted' %
              (title))
        return redirect(url_for('admin_page_list'))
    flash('Page not found!')
    return redirect(url_for('admin'))  

## FILES

@app.route('/admin/files')
@login_required
def admin_file_list():
    files = File.query.order_by(File.name)
    return render_template('admin/file_list.html',
                           files=files)
                                               
@app.route('/admin/files/<slug>', methods=['GET', 'POST'])
@login_required
def admin_file_item(slug):
    file = File() if slug == 'add' else File.query.filter_by(slug=slug).first()
    form = FileForm()
    if form.validate_on_submit():
        if 'file' in request.files and request.files['file'].filename != '':
            filename = adhocfiles.save(request.files['file'])
            s3.upload('adhocfiles/' + filename,open(adhocfiles.path(filename),'rb'))
            file.filename = filename
        file.name = form.name.data
        if slug == 'add':
            file.slug = slugify(file.name,to_lower=True)
            db.session.add(file)
        db.session.commit()
    	flash('File "%s" saved' %
              (form.name.data))
        return redirect( 'admin/files' )
    else:
        #url = adhocfiles.url(file.filename) if file.filename else None
        url = app.config['S3_URL'] + 'adhocfiles/' + file.filename if file.filename else None
        
        if request.method == 'GET':
            form.name.data = file.name
    
    return render_template('admin/file_item.html', 
                           id=file.id,
                           filename=file.filename,
                           url=url,
                           slug=file.slug,
                           form=form)
 

@app.route('/admin/files/delete/<id>')
@login_required
def admin_file_delete(id):
    file = File.query.filter_by(id=id).first()
    if file is not None:
        if file.filename:
            s3.delete('adhocfiles/' + file.filename)
        name = file.name
        db.session.delete(file)
        db.session.commit()
        flash('File "%s" deleted' %
              (name))
        return redirect(url_for('admin_file_list'))
    flash('File not found!')
    return redirect(url_for('admin'))  

@app.route('/admin/files/removefile/<id>')
@login_required
def admin_file_removefile(id):
    file = File.query.filter_by(id=id).first()
    if file is not None:
        #path = adhocfiles.path(file.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if file.filename:
            s3.delete('adhocfiles/' + file.filename)
        file.filename = None
        db.session.commit()
        return redirect(url_for('admin_file_item',slug=file.slug))
    flash('File not found!')
    return redirect(url_for('admin'))   


## SLIDES

@app.route('/admin/slides')
@login_required
def admin_slide_list():
    slides = Slide.query.order_by(Slide.heading)
    return render_template('admin/slide_list.html',
                           slides=slides)
                                               
@app.route('/admin/slides/<id>', methods=['GET', 'POST'])
@login_required
def admin_slide_item(id):
    slide = Slide() if id == 'add' else Slide.query.filter_by(id=id).first()
    form = SlideForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            imagename = slideimages.save(request.files['image'])
            s3.upload('slideimages/' + imagename,open(slideimages.path(imagename),'rb'))
            slide.imagename = imagename
        slide.heading = form.heading.data
        slide.subheading = form.subheading.data
        slide.link = form.link.data
        slide.active = form.active.data
        if id == 'add':
            db.session.add(slide)
        db.session.commit()
    	flash('Slide "%s" saved' %
              (form.heading.data))
        return redirect(url_for('admin_slide_list'))
    else:
        #url = slideimages.url(slide.imagename) if slide.imagename else None
        url = app.config['S3_URL'] + 'slideimages/' + slide.imagename if slide.imagename else None
        
        if request.method == 'GET':
            form.heading.data = slide.heading
            form.subheading.data = slide.subheading
            form.link.data = slide.link
            form.active.data = slide.active
    
    return render_template('admin/slide_item.html',
                           id=slide.id,
                           url=url,
                           form=form)
 

@app.route('/admin/slides/delete/<id>')
@login_required
def admin_slide_delete(id):
    slide = Slide.query.filter_by(id=id).first()
    if slide is not None:
        if slide.imagename:
            s3.delete('slideimages/' + slide.imagename)
        title = page.heading
        db.session.delete(slide)
        db.session.commit()
        flash('Slide "%s" deleted' %
              (title))
        return redirect(url_for('admin_slide_list'))
    flash('Slide not found!')
    return redirect(url_for('admin'))  

@app.route('/admin/slides/removeimage/<id>')
@login_required
def admin_slide_removeimage(id):
    slide = Slide.query.filter_by(id=id).first()
    if slide is not None:
        #path = slideimages.path(slide.imagename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if slide.imagename:
            s3.delete('slideimages/' + slide.imagename)
        slide.imagename = None
        db.session.commit()
        return redirect(url_for('admin_slide_item',id=id))
    flash('Slide not found!')
    return redirect(url_for('admin')) 


## COUNTRIES

@app.route('/admin/projects')
@login_required
def admin_country_list():
    countries = Country.query.order_by(Country.name)
    return render_template('admin/country_list.html',
                           countries=countries)
                                               
@app.route('/admin/projects/<slug>', methods=['GET', 'POST'])
def admin_country_item(slug):
    country = Country() if slug == 'add' else Country.query.filter_by(slug=slug).first()
    form = CountryForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = countryimages.save(request.files['image'])
            s3.upload('countryimages/' + filename,open(countryimages.path(filename),'rb'))
            country.filename = filename
        if 'codebook' in request.files and request.files['codebook'].filename != '':
            codebookfilename = codebookfiles.save(request.files['codebook'])
            s3.upload('codebookfiles/' + codebookfilename,open(codebookfiles.path(codebookfilename),'rb'))
            country.codebookfilename = codebookfilename
        country.name = form.name.data
        country.short_name = form.short_name.data
        country.principal = form.principal.data
        country.email = form.email.data
        country.location = form.location.data
        country.heading = form.heading.data
        country.about = form.about.data
        country.datasets_intro = form.datasets_intro.data
        country.embed_url = form.embed_url.data
        country.sponsoring_institutions = form.sponsoring_institutions.data
        
        #app.logger.debug(form.sponsoring_institutions.data)
        
        if slug == 'add':
            country.slug = slugify(country.short_name,to_lower=True)
            db.session.add(country)
        db.session.commit()
    	flash('Country "%s" saved' %
              (form.name.data))
        return redirect( url_for('admin_country_item',slug=current_user.country.slug) if current_user.country else url_for('admin_country_list') )
    else:
        #url = countryimages.url(country.filename) if country.filename else None
        url = app.config['S3_URL'] + 'countryimages/' + country.filename if country.filename else None
        
        #codebookurl = codebookfiles.url(country.codebookfilename) if country.codebookfilename else None
        codebookurl = app.config['S3_URL'] + 'codebookfiles/' + country.codebookfilename if country.codebookfilename else None
        
        if request.method == 'GET':
            form.name.data = country.name
            form.short_name.data = country.short_name
            form.principal.data = country.principal
            form.email.data = country.email
            form.location.data = country.location
            form.heading.data = country.heading
            form.about.data = country.about
            form.datasets_intro.data = country.datasets_intro 
            form.embed_url.data = country.embed_url
            form.sponsoring_institutions.data = country.sponsoring_institutions
    
    return render_template('admin/country_item.html', 
                           id=country.id,
                           slug=country.slug,
                           url=url,
                           form=form,
                           codebookurl = codebookurl,
                           codebookfilename=country.codebookfilename)
 

@app.route('/admin/projects/delete/<id>')
@login_required
def admin_country_delete(id):
    country = Country.query.filter_by(id=id).first()
    if country is not None:
        if country.filename:
            s3.delete('countryimages/' + country.filename)
        if country.codebookfilename:
            s3.delete('codebookfiles/' + country.codebookfilename)
        title = country.name
        db.session.delete(country)
        db.session.commit()
        flash('Country "%s" deleted' %
              (title))
        return redirect(url_for('admin_country_list'))
    flash('Country not found!')
    return redirect(url_for('admin'))  

@app.route('/admin/projects/removeimage/<id>')
@login_required
def admin_country_removeimage(id):
    country = Country.query.filter_by(id=id).first()
    if country is not None:
        #path = countryimages.path(country.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if country.filename:
            s3.delete('countryimages/' + country.filename)
        country.filename = None
        db.session.commit()
        return redirect(url_for('admin_country_item',slug=country.slug))
    flash('Country not found!')
    return redirect(url_for('admin'))                         

@app.route('/admin/projects/removecodebook/<id>')
@login_required
def admin_country_removecodebook(id):
    country = Country.query.filter_by(id=id).first()
    if country is not None:
        #path = codebookfiles.path(country.codebookfilename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if country.codebookfilename:
            s3.delete('codebookfiles/' + country.codebookfilename)
        country.codebookfilename = None
        db.session.commit()
        return redirect(url_for('admin_country_item',slug=country.slug))
    flash('Country not found!')
    return redirect(url_for('admin'))


## USERS

@app.route('/admin/users')
@app.route('/admin/users/p/<int:page>')
@login_required
def admin_user_list(page=1):
    users = User.query.order_by(desc(User.country_id)).paginate(page, 10, False)
    #users = User.query.order_by(desc(User.country_id)).all()
    return render_template('admin/user_list.html',
                           users=users)
                                               
@app.route('/admin/users/<id>', methods=['GET', 'POST'])
@login_required
def admin_user_item(id):
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
        return redirect(url_for('admin_user_list'))
    else:
        if request.method == 'GET':
            form.name.data = user.name
            form.email.data = user.email
            form.password.data = user.password
            form.country.data = user.country
    
    return render_template('admin/user_item.html', 
                           id=user.id,
                           form=form)

@app.route('/admin/password', methods=['GET', 'POST'])
@login_required
def admin_password():
    user = current_user
    form = UserForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
    	flash('Password changed to "%s" -- please remember it!' % (user.password))
        return redirect(url_for('admin'))
    return render_template('admin/password.html', 
                           id=user.id,
                           form=form)
                           
                         
@app.route('/admin/users/delete/<id>')
@login_required
def admin_user_delete(id):
    user = User.query.filter_by(id=id).first()
    if user is not None:
        name = user.name
        db.session.delete(user)
        db.session.commit()
        flash('User "%s" deleted' %
              (user.name))
        return redirect(url_for('admin_user_list'))
    flash('User not found!')
    return redirect(url_for('admin'))  

## NEWS

@app.route('/admin/projects/<slug>/news')
@app.route('/admin/projects/<slug>/news/p/<int:page>')
@login_required
def admin_news_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    news = News.query.filter_by(country_id=country.id).order_by(desc(News.saved_date)).paginate(page, 10, False)
    #news = News.query.all()
    return render_template('admin/news_list.html',
                           country=country,
                           news=news)
  #NNN                  
@app.route('/admin/projects/<slug>/news/<id>', methods=['GET', 'POST'])
@login_required
def admin_news_item(slug,id):
    country = Country.query.filter_by(slug=slug).first()
    news = News() if id == 'add' else News.query.filter_by(id=id).first()
    form = NewsForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = newsimages.save(request.files['image'])
            s3.upload('newsimages/' + filename,open(newsimages.path(filename),'rb'))
            news.filename = filename
        news.title = form.title.data
        news.content = form.content.data
        if id == 'add':
            news.slug = slugify(news.title,to_lower=True)
            news.country_id = country.id
            db.session.add(news)
        news.saved_date = datetime.utcnow()
        db.session.commit()
    	flash('News item "%s" saved' %
              (form.title.data))
        return redirect(url_for('admin_news_list',slug=slug))
    else:
        #url = newsimages.url(news.filename) if news.filename else None
        url = app.config['S3_URL'] + 'newsimages/' + news.filename if news.filename else None
        if request.method == 'GET':
            form.title.data = news.title
            form.content.data = news.content
    
    return render_template('admin/news_item.html', 
                           id=news.id,
                           country=country,
                           slug=slug,
                           url=url,
                           form=form)

@app.route('/admin/projects/<slug>/news/delete/<id>')
@login_required
def admin_news_delete(slug,id):
    news = News.query.filter_by(id=id).first()
    if news is not None:
        if news.filename:
            s3.delete('newsimages/' + news.filename)
        title = news.title
        db.session.delete(news)
        db.session.commit()
        flash('News item "%s" deleted' %
              (title))
        return redirect(url_for('admin_news_list',slug=slug))
    flash('News not found!')
    return redirect(url_for('admin'))  

@app.route('/admin/projects/<slug>/news/removeimage/<id>')
@login_required
def admin_news_removeimage(slug,id):
    news = News.query.filter_by(id=id).first()
    if news is not None:
        #path = newsimages.path(news.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if news.filename:
            s3.delete('newsimages/' + news.filename)
        news.filename = None
        db.session.commit()
        return redirect(url_for('admin_news_item',slug=slug,id=id))
    flash('News not found!')
    return redirect(url_for('admin')) 

## RESEARCH



@app.route('/admin/projects/<slug>/research')
@app.route('/admin/projects/<slug>/research/p/<int:page>')
@login_required
def admin_research_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    research = Research.query.filter_by(country_id=country.id).order_by(desc(Research.saved_date)).paginate(page, 10, False)
    return render_template('admin/research_list.html', 
                           country=country,
                           research=research)

@app.route('/admin/projects/<slug>/research/<id>', methods=['GET', 'POST'])
@login_required
def admin_research_item(slug,id):
    country = Country.query.filter_by(slug=slug).first()
    research = Research() if id == 'add' else Research.query.filter_by(id=id).first()
    form = ResearchForm()
    if form.validate_on_submit():
        if 'file' in request.files and request.files['file'].filename != '':
            filename = researchfiles.save(request.files['file'])
            s3.upload('researchfiles/' + filename,open(researchfiles.path(filename),'rb'))
            research.filename = filename
        if 'image' in request.files and request.files['image'].filename != '':
            imagename = researchimages.save(request.files['image'])
            s3.upload('researchimages/' + imagename,open(researchimages.path(imagename),'rb'))
            research.imagename = imagename
        research.title = form.title.data
        research.body = form.body.data
        research.featured = form.featured.data
        if id == 'add':
            research.country_id = country.id
            db.session.add(research)
        research.saved_date = datetime.utcnow()
        db.session.commit()
    	flash('Research item "%s" saved' %
              (form.title.data))
        return redirect(url_for('admin_research_list',slug=slug))
    else:
        #fileurl = researchfiles.url(research.filename) if research.filename else None
        #imageurl = researchimages.url(research.imagename) if research.imagename else None
        fileurl = app.config['S3_URL'] + 'researchfiles/' + research.filename if research.filename else None
        imageurl = app.config['S3_URL'] + 'researchimages/' + research.imagename if research.imagename else None
        
        if request.method == 'GET':
            form.title.data = research.title
            form.body.data = research.body
            form.featured.data = research.featured
    
    return render_template('admin/research_item.html',
                           slug=slug,
                           filename=research.filename,
                           imagename=research.imagename,
                           country=country,
                           id=research.id,
                           fileurl=fileurl,
                           imageurl=imageurl,
                           form=form)

@app.route('/admin/projects/<slug>/research/delete/<id>')
@login_required
def admin_research_delete(slug,id):
    research = Research.query.filter_by(id=id).first()
    if research is not None:
        if research.filename:
            s3.delete('researchfiles/' + research.filename)
        if research.imagename:
            s3.delete('researchimages/' + research.imagename)
        title = research.title
        db.session.delete(research)
        db.session.commit()
        flash('Research item "%s" deleted' %
              (title))
        return redirect(url_for('admin_research_list',slug=slug))
    flash('Research not found!')
    return redirect(url_for('admin')) 

@app.route('/admin/projects/<slug>/research/removefile/<id>')
@login_required
def admin_research_removefile(slug,id):
    research = Research.query.filter_by(id=id).first()
    if research is not None:
        #path = researchfiles.path(research.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if research.filename:
            s3.delete('researchfiles/' + research.filename)
        research.filename = None
        db.session.commit()
        return redirect(url_for('admin_research_item',slug=slug,id=id))
    flash('Research not found!')
    return redirect(url_for('admin'))

@app.route('/admin/projects/<slug>/research/removeimage/<id>')
@login_required
def admin_research_removeimage(slug,id):
    research = Research.query.filter_by(id=id).first()
    if research is not None:
        #path = researchimages.path(research.imagename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if research.imagename:
            s3.delete('researchimages/' + research.imagename)
        research.imagename = None
        db.session.commit()
        return redirect(url_for('admin_research_item',slug=slug,id=id))
    flash('Research not found!')
    return redirect(url_for('admin')) 

## STAFF
@app.route('/admin/projects/<slug>/staff')
@app.route('/admin/projects/<slug>/staff/p/<int:page>')
@login_required
def admin_staff_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    staff = Staff.query.filter_by(country_id=country.id).order_by(Staff.sort_order).paginate(page, 10, False)
    return render_template('admin/staff_list.html', 
                           country=country,
                           staff=staff)

@app.route('/admin/projects/<slug>/staff/<id>', methods=['GET', 'POST'])
@login_required
def admin_staff_item(slug,id):
    country = Country.query.filter_by(slug=slug).first()
    staff = Staff() if id == 'add' else Staff.query.filter_by(id=id).first()
    form = StaffForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = staffimages.save(request.files['image'])
            s3.upload('staffimages/' + filename,open(staffimages.path(filename),'rb'))
            staff.filename = filename
        staff.name = form.name.data
        staff.title = form.title.data
        staff.institution = form.institution.data
        staff.sort_order = form.sort_order.data
        staff.body = form.body.data
        if id == 'add':
            staff.country_id = country.id
            db.session.add(staff)
        db.session.commit()
    	flash('Staff member "%s" saved' %
              (form.name.data))
        return redirect(url_for('admin_staff_list',slug=slug))
    else:
        #url = staffimages.url(staff.filename) if staff.filename else None
        url = app.config['S3_URL'] + 'staffimages/' + staff.filename if staff.filename else None
        
        
        if request.method == 'GET':
            form.name.data = staff.name
            form.title.data = staff.title
            form.institution.data = staff.institution
            form.sort_order.data = staff.sort_order
            form.body.data = staff.body
    
    return render_template('admin/staff_item.html',
                           slug=slug,
                           filename=staff.filename,
                           country=country,
                           id=staff.id,
                           url=url,
                           form=form)

@app.route('/admin/projects/<slug>/staff/delete/<id>')
@login_required
def admin_staff_delete(slug,id):
    staff = Staff.query.filter_by(id=id).first()
    if staff is not None:
        if staff.filename:
            s3.delete('staffimages/' + staff.filename)
        title = staff.title
        db.session.delete(staff)
        db.session.commit()
        flash('Staff member "%s" deleted' %
              (title))
        return redirect(url_for('admin_staff_list',slug=slug))
    flash('Staff member not found!')
    return redirect(url_for('admin'))

@app.route('/admin/projects/<slug>/staff/removeimage/<id>')
@login_required
def admin_staff_removefile(slug,id):
    staff = Staff.query.filter_by(id=id).first()
    if staff is not None:
        #path = staffimages.path(staff.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if staff.filename:
            s3.delete('staffimages/' + staff.filename)
        staff.filename = None
        db.session.commit()
        return redirect(url_for('admin_staff_item',slug=slug,id=id))
    flash('Staff member not found!')
    return redirect(url_for('admin'))


## ANALYTICS

@app.route('/admin/projects/<slug>/analytics')
@login_required
def admin_analytics(slug):
    country = Country.query.filter_by(slug=slug).first()
    return render_template('admin/analytics.html',
                           country=country)


## DATASETS

@app.route('/admin/projects/<slug>/datasets')
@app.route('/admin/projects/<slug>/datasets/<int:tab>')
@app.route('/admin/projects/<slug>/datasets/<int:tab>/p/<int:page>')
@login_required
def admin_dataset_list(slug,tab=1,page=1):
    country = Country.query.filter_by(slug=slug).first()
    datasets_policy = Dataset.query.filter_by(country_id=country.id).filter_by(budget=False).order_by(desc(Dataset.saved_date)).paginate(page, 20, False)
    datasets_budget = Dataset.query.filter_by(country_id=country.id).filter_by(budget=True).order_by(desc(Dataset.saved_date)).paginate(page, 20, False)
    datasets_download = Staticdataset.query.filter_by(country_id=country.id).order_by(desc(Staticdataset.saved_date)).paginate(page, 20, False)
    return render_template('admin/dataset_list.html',
                           country=country,
                           tab=tab,
                           datasets_policy=datasets_policy,
                           datasets_budget=datasets_budget,
                           datasets_download=datasets_download)



# routes for static ("Download only") datasets

@app.route('/admin/staticdataset/upload', methods=['POST'])
@login_required
def admin_staticdataset_upload():
    retval = {}
    datasetfilename = datasetfiles.save(request.files['file'])
    retval['filename'] = datasetfilename
    resp = Response(dumps(retval), status=200, mimetype='application/json')
    return resp
    
@app.route('/admin/projects/<slug>/staticdataset/<id>', methods=['GET', 'POST'])
@login_required
def admin_staticdataset_item(slug,id):
    
    country = Country.query.filter_by(slug=slug).first()
    dataset = Staticdataset() if (id == 'add') else Staticdataset.query.filter_by(id=id).first()
    form = StaticDatasetForm()
    
    content = False
    if 'content' in request.form and request.form['content'] != '':
        content = request.form['content']
        s3.upload('datasetfiles/' + content,open(datasetfiles.path(content),'rb'))
        dataset.datasetfilename = content
    
    if form.validate_on_submit():
        
        if 'codebook' in request.files and request.files['codebook'].filename != '':
            codebookfilename = codebookfiles.save(request.files['codebook'])
            s3.upload('codebookfiles/' + codebookfilename,open(codebookfiles.path(codebookfilename),'rb'))
            dataset.codebookfilename = codebookfilename
        
        if content:
            dataset.ready = True
            newdata = True
        
        dataset.display = form.display.data
        dataset.short_display = form.short_display.data
        dataset.description = form.description.data
        dataset.category = form.category.data
        
        tab = 3
        
        if id == 'add':
            dataset.country_id = country.id
            try:
                db.session.add(dataset) 
            except:
                flash('Something went wrong, dataset not saved!')
                return redirect(url_for('admin_dataset_list',slug=slug,tab=tab))
    
        dataset.saved_date = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Dataset "%s" saved' % (form.display.data))
        except:
            flash('Something went wrong, dataset not saved!')
            return redirect(url_for('admin_dataset_list',slug=slug,tab=tab))
            
        return redirect(url_for('admin_dataset_list',slug=slug,tab=tab))
    


    else:
    
        #dataseturl= datasetfiles.url(dataset.datasetfilename) if dataset.datasetfilename else None
        #codebookurl = codebookfiles.url(dataset.codebookfilename) if dataset.codebookfilename else None
        dataseturl= app.config['S3_URL'] + 'datasetfiles/' + dataset.datasetfilename if dataset.datasetfilename else None
        codebookurl = app.config['S3_URL'] + 'codebookfiles/' + dataset.codebookfilename if dataset.codebookfilename else None
        
        
        if request.method == 'GET':
            form.display.data = dataset.display
            form.short_display.data = dataset.short_display
            form.description.data = dataset.description
            form.category.data = dataset.category
    
    return render_template('admin/staticdataset_item.html', 
                           id=dataset.id,
                           country=country,
                           slug=slug,
                           ready=dataset.ready,
                           dataseturl=dataseturl,
                           datasetfilename=dataset.datasetfilename,
                           codebookurl=codebookurl,
                           codebookfilename=dataset.codebookfilename,
                           form=form)

@app.route('/admin/projects/<slug>/staticdataset/delete/<id>')
@login_required
def admin_staticdataset_delete(slug,id):
    dataset = Staticdataset.query.filter_by(id=id).first()
    if dataset is not None:
        if dataset.datasetfilename:
            s3.delete('datasetfiles/' + dataset.datasetfilename)
        if dataset.codebookfilename:
            s3.delete('codebookfiles/' + dataset.codebookfilename)
        title = dataset.display
        db.session.delete(dataset)
        db.session.commit()
        flash('Dataset "%s" deleted' %
              (title))
        return redirect(url_for('admin_dataset_list',slug=slug,tab=3))
    flash('Dataset not found!')
    return redirect(url_for('admin'))  

@app.route('/admin/projects/<slug>/staticdataset/remove/<id>')
@login_required
def admin_staticdataset_removecontent(slug,id):
    dataset = Staticdataset.query.filter_by(id=id).first()
    if dataset is not None:
        #path = datasetimages.path(dataset.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if dataset.datasetfilename:
            s3.delete('datasetfiles/' + dataset.datasetfilename)
        dataset.datasetfilename = None
        dataset.ready = False
        db.session.commit()
        return redirect(url_for('admin_staticdataset_item',slug=slug,id=id))
    flash('Dataset not found!')
    return redirect(url_for('admin')) 

@app.route('/admin/projects/<slug>/staticcodebook/remove/<id>')
@login_required
def admin_staticdataset_removecodebook(slug,id):
    dataset = Staticdataset.query.filter_by(id=id).first()
    if dataset is not None:
        #path = codebookfiles.path(dataset.codebookfilename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if dataset.codebookfilename:
            s3.delete('codebookfiles/' + dataset.codebookfilename)
        dataset.codebookfilename = None
        db.session.commit()
        return redirect(url_for('admin_staticdataset_item',slug=slug,id=id))
    flash('Dataset not found!')
    return redirect(url_for('admin'))

# routes for REAL datasets, i.e. the ones in the trends tool

@app.route('/admin/dataset/upload/<type>', methods=['POST'])
@login_required
def admin_dataset_upload(type):
    #dataset = Dataset.query.filter_by(id=id).first()
    #if dataset is not None:
    retval = {}
    datasetfilename = datasetfiles.save(request.files['file'])
    datasetfilepath = datasetfiles.path(datasetfilename)
    #didit = convert_to_utf8(datasetfilepath)
    csvfile = open(datasetfilepath, 'rU')
    reader = csv.DictReader(csvfile)
    #reader.fieldnames = [item.lower() for item in reader.fieldnames]
    errors = ''
    
    if reader.fieldnames:
        #required_fieldnames = ['id','year','majortopic','subtopic']
        if type=='policy':
            required_fieldnames = ['id','year','majortopic']
        if type=='budget':
            required_fieldnames = ['id','year','majorfunction','amount']
        for required_fieldname in required_fieldnames:
            if required_fieldname not in reader.fieldnames:
                errors += 'Missing column: "' + required_fieldname + '" '
    if len(errors) > 0: #validation failed
        retval['error'] = errors
        resp = Response(dumps(retval), status=412, mimetype='application/json')
        return resp
    
    #validation succeeded
    retval['filename'] = datasetfilename
    resp = Response(dumps(retval), status=200, mimetype='application/json')
    return resp
                     
@app.route('/admin/projects/<slug>/dataset/<id>', methods=['GET', 'POST'])
@login_required
def admin_dataset_item(slug,id):
    
    newdata = False
    country = Country.query.filter_by(slug=slug).first()
    dataset = Dataset() if (id == 'add' or id=='addbudget') else Dataset.query.filter_by(id=id).first()
    form = DatasetForm()
    
    if id == 'addbudget':
        dataset.budget = True
        
    content = False
    if 'content' in request.form and request.form['content'] != '':
        content = request.form['content']
        s3.upload('datasetfiles/' + content,open(datasetfiles.path(content),'rb'))
        dataset.datasetfilename = content
        
    form.fieldnames=[]
    if dataset.datasetfilename:
        datasetfilepath = datasetfiles.path(dataset.datasetfilename)
        csvfile = open(datasetfilepath, 'rU')
        reader = csv.DictReader(csvfile)
        form.fieldnames = [item.lower() for item in reader.fieldnames]
        
    form.topicsfieldnames=[]
    if 'topics' in request.files and request.files['topics'].filename != '':
        topicsfilename = topicsfiles.save(request.files['topics'])
        topicsfilepath = topicsfiles.path(topicsfilename)
        s3.upload('topicsfiles/' + topicsfilename,open(topicsfilepath,'rb'))
        try:
            didit = convert_to_utf8(topicsfilepath)
        except:
            didit = False
        if (didit == False):
            flash('Topics not converted to UTF-8!')
            return redirect(url_for('admin_dataset_list',slug=slug))
        topicscsvfile = open(topicsfilepath, 'rU')
        topicsreader = csv.DictReader(topicscsvfile)
        form.topicsfieldnames = [item.lower() for item in topicsreader.fieldnames]
    
        
    if form.validate_on_submit():
        
        if 'codebook' in request.files and request.files['codebook'].filename != '':
            codebookfilename = codebookfiles.save(request.files['codebook'])
            s3.upload('codebookfiles/' + codebookfilename,open(codebookfiles.path(codebookfilename),'rb'))
            dataset.codebookfilename = codebookfilename
        
        if content:
        
            filters = []
            for fieldname in form.fieldnames:
                if fieldname.split('_')[0] == 'filter':
                    filters.append(fieldname)
            dataset.filters = filters
            thedata = []
            for row in reader:
                if 'count' in form.fieldnames:
                    if row['id'] and row['year'] and row['majortopic'] and row['count']:
                        thedata.append(row)
                elif 'amount' in form.fieldnames:
                    if row['id'] and row['year'] and row['majorfunction'] and row['amount']:
                        thedata.append(row)
                elif 'percent' in form.fieldnames:
                    if row['id'] and row['year'] and row['majortopic'] and row['percent']:
                        row['percent'] = float(row['percent'])
                        thedata.append(row)
                else:
                    if row['id'] and row['year'] and row['majortopic']:
                        thedata.append(row)
                    
            dataset.content = thedata
            dataset.ready = True
            newdata = True
        
        if 'topics' in request.files and request.files['topics'].filename != '':
        
            dataset.topicsfilename = topicsfilename
            thedata = []
            majorfunctions=[]
            subfunctions=[]
            for row in topicsreader:
                if row['subfunction'] == '':
                    majorfunctions.append(row)
                else:
                    subfunctions.append(row)
            
            for row in majorfunctions:
                therow = {}
                therow['id'] = row['majorfunction']
                therow['name'] = row['shortname']
                thesubs = []
                for subrow in subfunctions:
                    if subrow['majorfunction'] == row['majorfunction']:
                        thesub = {}
                        thesub['id'] = subrow['subfunction']
                        thesub['name'] = subrow['shortname']
                        thesubs.append(thesub)
                if len(thesubs) > 0:
                    therow['subtopics'] = thesubs
                
                thedata.append(therow)
                
            dataset.topics = thedata 
            
        dataset.display = form.display.data
        dataset.short_display = form.short_display.data
        dataset.description = form.description.data
        dataset.unit = form.unit.data
        dataset.source = form.source.data
        if dataset.budget:
            dataset.budgetcategory = form.budgetcategory.data
            dataset.category_id = 7
        else:
            dataset.category = form.category.data
            
        dataset.aggregation_level = 1 if dataset.budget else form.aggregation_level.data
        
        tab = 2 if dataset.budget else 1
        
        if id == 'add' or id == 'addbudget':
            dataset.country_id = country.id
            try:
                db.session.add(dataset) 
            except:
                flash('Something went wrong, dataset not saved!')
                return redirect(url_for('admin_dataset_list',slug=slug,tab=tab))
                
        dataset.saved_date = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Dataset "%s" saved' % (form.display.data))
        except:
            flash('Something went wrong, dataset not saved!')
            return redirect(url_for('admin_dataset_list',slug=slug,tab=tab))
            
        if newdata == True:
            update_stats(db,dataset.id,country.id)
            
        return redirect(url_for('admin_dataset_list',slug=slug,tab=tab))
        
    else:
    
        #dataseturl= datasetfiles.url(dataset.datasetfilename) if dataset.datasetfilename else None
        #codebookurl = codebookfiles.url(dataset.codebookfilename) if dataset.codebookfilename else None
        #topicsurl = topicsfiles.url(dataset.topicsfilename) if dataset.topicsfilename else None
        
        dataseturl= app.config['S3_URL'] + 'datasetfiles/' + dataset.datasetfilename if dataset.datasetfilename else None
        codebookurl = app.config['S3_URL'] + 'codebookfiles/' + dataset.codebookfilename if dataset.codebookfilename else None
        topicsurl = app.config['S3_URL'] + 'topicsfiles/' + dataset.topicsfilename if dataset.topicsfilename else None
        
        if request.method == 'GET':
            form.display.data = dataset.display
            form.short_display.data = dataset.short_display
            form.description.data = dataset.description
            form.unit.data = dataset.unit
            form.source.data = dataset.source
            form.category.data = dataset.category
            form.budgetcategory.data = dataset.budgetcategory
            form.topics.data = dataset.topics
            if dataset.budget==False:
                form.aggregation_level.data = str(dataset.aggregation_level)
            
    template = 'admin/budget_dataset_item.html' if dataset.budget else 'admin/dataset_item.html'
    
    return render_template(template, 
                           id=dataset.id,
                           country=country,
                           slug=slug,
                           ready=dataset.ready,
                           dataseturl=dataseturl,
                           datasetfilename=dataset.datasetfilename,
                           codebookurl=codebookurl,
                           codebookfilename=dataset.codebookfilename,
                           topicsurl=topicsurl,
                           topicsfilename=dataset.topicsfilename,
                           form=form)

@app.route('/admin/projects/<slug>/dataset/delete/<id>')
@login_required
def admin_dataset_delete(slug,id):
    dataset = Dataset.query.filter_by(id=id).first()
    if dataset is not None:
        if dataset.datasetfilename:
            s3.delete('datasetfiles/' + dataset.datasetfilename)
        if dataset.codebookfilename:
            s3.delete('codebookfiles/' + dataset.codebookfilename)
        if dataset.topicsfilename:
            s3.delete('topicsfiles/' + dataset.topicsfilename)
        title = dataset.display
        db.session.delete(dataset)
        db.session.commit()
        country_id = dataset.country_id
        # update stats for the whole country
        sql = """
        UPDATE country SET 
        stats_series = (SELECT COUNT(id) FROM dataset WHERE ready=true AND country_id=%s),
        stats_year_from = COALESCE( (SELECT MIN(stats_year_from) FROM dataset WHERE ready=true AND country_id=%s), 0),
        stats_year_to = COALESCE( (SELECT MAX(stats_year_to) FROM dataset WHERE ready=true AND country_id=%s), 0),
        stats_observations = COALESCE( (SELECT SUM(stats_observations) FROM dataset WHERE ready=true AND country_id=%s), 0)
        WHERE id = %s
        """
        cur = db.session.connection().connection.cursor()
        cur.execute(sql,[country_id,country_id,country_id,country_id,country_id])
        db.session.commit() 
        flash('Dataset "%s" deleted' %
              (title))
        return redirect(url_for('admin_dataset_list',slug=slug))
    flash('Dataset not found!')
    return redirect(url_for('admin'))  

@app.route('/admin/projects/<slug>/dataset/remove/<id>')
@login_required
def admin_dataset_removecontent(slug,id):
    dataset = Dataset.query.filter_by(id=id).first()
    if dataset is not None:
        #path = datasetimages.path(dataset.filename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if dataset.datasetfilename:
            s3.delete('datasetfiles/' + dataset.datasetfilename)
        dataset.datasetfilename = None
        dataset.ready = False
        db.session.commit()
        return redirect(url_for('admin_dataset_item',slug=slug,id=id))
    flash('Dataset not found!')
    return redirect(url_for('admin')) 

@app.route('/admin/projects/<slug>/codebook/remove/<id>')
@login_required
def admin_dataset_removecodebook(slug,id):
    dataset = Dataset.query.filter_by(id=id).first()
    if dataset is not None:
        #path = codebookfiles.path(dataset.codebookfilename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if dataset.codebookfilename:
            s3.delete('codebookfiles/' + dataset.codebookfilename)
        dataset.codebookfilename = None
        db.session.commit()
        return redirect(url_for('admin_dataset_item',slug=slug,id=id))
    flash('Dataset not found!')
    return redirect(url_for('admin'))

@app.route('/admin/projects/<slug>/topics/remove/<id>')
@login_required
def admin_dataset_removetopics(slug,id):
    #return redirect(url_for('admin_dataset_item',slug=slug,id=id))
    dataset = Dataset.query.filter_by(id=id).first()
    if dataset is not None:
        #path = topicsfiles.path(dataset.topicsfilename)
        #if os.path.isfile(path):
        #    os.remove(path)
        if dataset.topicsfilename:
            s3.delete('topicsfiles/' + dataset.topicsfilename)
        dataset.topicsfilename = None
        db.session.commit()
        return redirect(url_for('admin_dataset_item',slug=slug,id=id))
    flash('Dataset not found!')

######### API ROUTES

@app.route('/api/charts/<user>')
def api_charts(user):
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT slug, options, id FROM chart WHERE unpinned = False AND "user" = %(user)s ORDER BY "date"', {"user": user})
    return dumps(cur.fetchall())

@app.route('/api/projects')
def api_countries():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT DISTINCT ON (c.name) c.* FROM country c INNER JOIN dataset d ON c.id = d.country_id ORDER BY c.name""")
    #cur.execute("""SELECT * FROM country ORDER BY name""")
    return dumps(cur.fetchall())

@app.route('/api/budgetprojects')
def api_budgetprojects():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT DISTINCT ON (c.name) c.* FROM country c INNER JOIN dataset d ON c.id = d.country_id WHERE d.budget=True AND d.ready=TRUE ORDER BY c.name""")
    countries = cur.fetchall()
    
    for country in countries:
        sql = """
        SELECT 
            d.id,
            d.budgetcategory_id AS category,
            d.topics AS topics,
            d.short_display AS name,
            c.short_name AS country,
            d.filters AS filters,
            d.unit AS unit,
            d.aggregation_level AS aggregation_level
        FROM dataset d
        INNER JOIN country c ON d.country_id = c.id
        WHERE d.country_id = %(country_id)s 
        AND d.ready=TRUE
        AND d.budget= TRUE
        ORDER BY d.short_display
        """
        cur.execute(sql,{"country_id": country['id']})
        datasets = cur.fetchall()
        country['datasets'] = datasets
        
    return dumps(countries)

@app.route('/api/categories')
def api_categories():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    #cur.execute("""SELECT DISTINCT(c.*) FROM category c INNER JOIN dataset d ON c.id = d.category_id ORDER BY c.name""")
    cur.execute("""SELECT c.id as category_id, c.* FROM category c ORDER BY c.id""")
    return dumps(cur.fetchall())

@app.route('/api/topics')
def api_topics():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
    SELECT Concat(Trim(To_char(m.majortopic, '999')), '_', m.shortname) 
       AS topic
       , 
       Array_agg( 
       Concat(Trim(To_char(t.subtopic, '9999')), '_', t.shortname)) AS 
       subtopics 
    FROM   major_topics m 
           JOIN sub_topics t 
             ON m.majortopic = t.majortopic 
    GROUP  BY m.id,
	      m.shortname,
              m.majortopic 
    ORDER  BY m.id
    """)
    return dumps(cur.fetchall())

@app.route('/api/datasets')
def api_datasets(flag = None):
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    sql = """
    SELECT d.id,
    d.category_id AS category,  
    d.short_display AS name,
    c.short_name AS country,
    d.filters AS filters,
    d.unit AS unit,
    d.aggregation_level AS aggregation_level
    FROM dataset d
    INNER JOIN country c ON d.country_id = c.id
    WHERE d.ready=TRUE
    AND d.budget=FALSE
    ORDER BY d.short_display
    """
    cur.execute(sql)
    return dumps(cur.fetchall())

@app.route('/api/drilldown/<dataset>/<flag>/<topic>/<year>')
def api_drilldown(dataset,flag,topic,year):
    
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if flag=='topic':
        sub = False
    elif flag=='subtopic':
        sub = True
    else:
        abort(404)
    
    # DRILLDOWN
    
    sql = """
    select datarow->>'source' as source, datarow->>'description' as description
    from (
      select jsonb_array_elements(content)
      from dataset WHERE dataset.id = %s
    ) s(datarow)
    """
    
    if (int(year) < 1000): # HACK!! to handle congress time periods, which are ~80-120
        frm = (int(year) * 2) + 1787
        to = (int(year) * 2) + 1788    
    else:
        frm = year
        to = year
    
    where = instances_get_where(db,dataset,sub,topic,str(frm),str(to))
    sql = sql + where
    cur.execute(sql,[dataset])
    
    return dumps(cur.fetchall())


@app.route('/api/instances/<dataset>/<flag>/<topic>/<frm>/<to>')
def api_instances(dataset,flag,topic,frm,to):
    
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if flag=='topic':
        sub = False
    elif flag=='subtopic':
        sub = True
    else:
        abort(404)
    
    # INSTANCES
    
    sql = """
    select datarow
    from (
      select jsonb_array_elements(content)
      from dataset WHERE dataset.id = %s
    ) s(datarow)
    """
    
    if (int(frm) < 1000): # HACK!! to handle congress time periods, which are ~80-120
        frm = (int(frm) * 2) + 1787
        to = (int(to) * 2) + 1788
    
    where = instances_get_where(db,dataset,sub,topic,str(frm),str(to))
    
    sql = sql + where
    
    #app.logger.debug(sql)
    
    cur.execute(sql,[dataset])
    
    def generate():
        firstrow = cur.fetchone()['datarow']
        yield ','.join(firstrow.keys()) + '\n'
        yield '"' + '","'.join(map(str,firstrow.values())) + '"' + '\n'
        for u in cur.fetchall():
            yield '"' + '","'.join(map(str,u['datarow'].values())) + '"' + '\n'
            
    return Response(generate(), mimetype='text/csv')
    
    
@app.route('/api/measures/dataset/<dataset>/<flag>/<topic>')
@app.route('/api/measures/dataset/<dataset>/<flag>/<topic>')
def api_measures(dataset,flag,topic):
    
    if flag=='topic':
        sub = False
    elif flag=='subtopic':
        sub = True
    else:
        abort(404)
    
    #app.logger.debug(flag);
    
    # CHECK CACHE
    #cached_path = '/var/www/cap/datacache/' + dataset + '-' + topic + request.query_string + '-measures.json'
    #app.logger.debug(cached_path);
    
    #if (os.path.isfile(cached_path)):
    #    return send_file(cached_path)
    
    # NO CACHE, GO TO THE DB!!
    
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    data = {}
    
    # RETRIEVE METADATA
    sql = """
    select filters, aggregation_level, budget from dataset WHERE dataset.id = %s
    """
    cur.execute(sql,[dataset])
    r = cur.fetchone()
    filters = r["filters"] if r["filters"] != None else []
    
    filter_predicates = []
    for filter in filters:
        filterval = request.args.get(filter)
        if (filterval != None):
            filter_predicates.append("datarow->>'" + filter + "'='" + filterval + "'")
    
    #app.logger.debug(filter_predicates);
    
    topic_col = 'subtopic' if sub else 'majortopic'
    
    if r["aggregation_level"] != 2:
        
        if r["aggregation_level"] == 1:
            
            if r["budget"]:
                topic_col = 'subfunction' if sub else 'majorfunction'
                count_col = 'amount'
            else:
                count_col = 'count'
            
            # TOTALS ALL TOPICS
    
            sql = "SELECT yt.year::int, SUM(yt." + count_col
            sql = sql + "::float) as total FROM (select datarow->>'year' AS year, datarow->>'"
            sql = sql + count_col + "' AS " + count_col
            sql = sql + """
            FROM (
              select jsonb_array_elements(content)
              from dataset WHERE dataset.id = %s
             ) s(datarow)
            WHERE 1=1"""
            sql = sql + """
            AND datarow->>'year' ~ '^[0-9]'
            AND datarow->>'year' != '0'
            ) yt
            GROUP BY yt.year  ORDER by yt.year
            """
        
            cur.execute(sql,[dataset])
            rows = cur.fetchall()
    
            totals = []
            for i, total in enumerate(d['total'] for d in rows): 
                totals.append(total)
    
    
            # CALCULATE years for which this dataset "has data" (for ANY topic)
            years = []
            for i, year in enumerate(d['year'] for d in rows): 
                years.append(year)
         
            data['years'] = years
    
    
            # COUNT THIS TOPIC
            
            if topic == '0':
                count = totals
            else :
                sql = "SELECT yt.year::int, SUM(yt." + count_col
                sql = sql + "::float) as cnt FROM (select datarow->>'year' AS year, datarow->>'"
                sql = sql + count_col + "' AS " + count_col
                sql = sql + """
                FROM (
                  select jsonb_array_elements(content)
                  from dataset WHERE dataset.id = %s
                 ) s(datarow)
                where datarow->>'""" + topic_col + "' = %s"
                sql = sql + """
                AND datarow->>'year' ~ '^[0-9]'
                AND datarow->>'year' != '0'
                ) yt
                GROUP BY yt.year  ORDER by yt.year
                """
            
                cur.execute(sql,[dataset,topic])
                rows = cur.fetchall()
    
                count = []
                for year in years:
                    found = next((item for item in rows if item['year'] == year), None)
                    if found is not None:
                        count.append(found['cnt'])
                    else:
                        count.append(0)
            data[count_col] = count
        
        else:
            
            # TOTALS ALL TOPICS
    
            sql = """
            SELECT yt.year::int, yt.total::int FROM (
            select datarow->>'year' AS year, COUNT(datarow->'id') as total
            from (
              select jsonb_array_elements(content)
              from dataset WHERE dataset.id = %s
            ) s(datarow)
            WHERE 1=1"""
    
            if len(filter_predicates) > 0:
                for pred in filter_predicates:
                    sql = sql + " AND " + pred 
    
            sql = sql + """
            AND datarow->>'year' ~ '^[0-9]'
            AND datarow->>'year' != '0'
            GROUP BY year) AS yt ORDER by year
            """
            
            #app.logger.debug(sql)
            
            cur.execute(sql,[dataset])
            rows = cur.fetchall()
    
            totals = []
            for i, total in enumerate(d['total'] for d in rows): 
                totals.append(total)
    
    
            # CALCULATE years for which this dataset "has data" (for ANY topic)
            years = []
            for i, year in enumerate(d['year'] for d in rows): 
                years.append(year)
         
            data['years'] = years
    
    
    
            # COUNT THIS TOPIC
            
            if topic == '0':
                count = totals
            else :
                sql = """
                SELECT yc.year::int, yc.cnt::int FROM (
                select datarow->>'year' AS year, COUNT(datarow->'id') as cnt
                from (
                select jsonb_array_elements(content)
                from dataset WHERE dataset.id = %s
                ) s(datarow)
                where datarow->>'""" + topic_col + "' = %s"
    
                if len(filter_predicates) > 0:
                    for pred in filter_predicates:
                        sql = sql + " AND " + pred 
            
                sql = sql + """
                AND datarow->>'year' ~ '^[0-9]'
                AND datarow->>'year' != '0'
                GROUP BY year) AS yc ORDER by year
                """
    
                cur.execute(sql,[dataset,topic])
                rows = cur.fetchall()
    
                count = []
                for year in years:
                    found = next((item for item in rows if item['year'] == year), None)
                    if found is not None:
                        count.append(found['cnt'])
                    else:
                        count.append(0)
            data['count'] = count
    
        
        # PERCENT CHANGE
        percent_change = [None]
        i = 0
        for c in count:
            i += 1
            if i < len(count):
                pc = float(count[i] - count[i - 1])/count[i - 1] if (count[i - 1] > 0) else None
                if pc is not None:
                    percent_change.append(float("{0:.2f}".format(100 * pc)))
                else:
                    percent_change.append(None)
        data['percent_change'] = percent_change

        percent_total = []
        i = 0
        for c in count:
            if i < len(count):
                pt = float(count[i])/totals[i] if (totals[i] > 0) else None
                if pt is not None:
                    percent_total.append(float("{0:.3f}".format(100 * pt)))
                    #percent_total.append(pt)
                else:
                    percent_total.append(None)
                i += 1
        data['percent_total'] = percent_total
    
    else:
        
        # OUR DATA IS STRAIGHT UP PERCENT TOTAL -- no other measures avail!!
    
        sql = """
        SELECT yc.year::int, yc.percent::text::float FROM (
        select datarow->>'year' AS year, datarow->'percent' as percent
        from (
        select jsonb_array_elements(content)
        from dataset WHERE dataset.id = %s
        ) s(datarow)
        where datarow->>'""" + topic_col + "' = %s"
        
        sql = sql + """
        AND datarow->>'year' ~ '^[0-9]'
        AND datarow->>'year' != '0'
        ) AS yc ORDER by year
            """

        cur.execute(sql,[dataset,topic])
        rows = cur.fetchall()
        
        years = []
        for i, year in enumerate(d['year'] for d in rows): 
            years.append(year)
        data['years'] = years
        
        percent_total = []
        for i, percent in enumerate(d['percent'] for d in rows): 
            percent_total.append(float("{0:.3f}".format(100 * percent)))    
        data['percent_total'] = percent_total
    
    # WRITE CACHE
    #with open(cached_path, 'w') as outfile:
    #    dump(data, outfile)
         
    return dumps(data)

# ONE OF EM  
@app.route('/<slug>')
@app.route('/<slug>/<pane>')
def country(slug,pane='about'):
    country = Country.query.filter_by(slug=slug).first()
    if country:
        countries = Country.query.filter(Country.id != country.id).order_by(Country.name).all()
        categories = Category.query.all()
        cats = []
        for category in categories:
            
            #app.logger.debug(category)
        
            datasets = [u.__dict__ for u in Dataset.query.filter_by(country_id=country.id).filter_by(category_id=category.id).filter_by(ready=True).all()]
            
            for u in Staticdataset.query.filter_by(category_id=category.id).filter_by(country_id=country.id).filter_by(category_id=category.id).all():
                datasets.append(u.__dict__)
            
            datasets = sorted(datasets, key=lambda k: k['display'])
            if len(datasets) > 0:
                setattr(category, 'datasets', datasets)
                cats.append(category)
        
        #budget_datasets = [u.__dict__ for u in Dataset.query.filter_by(country_id=country.id).filter_by(budget=True).filter_by(ready=True).all()]
        #if len(budget_datasets) > 0:
        #        cats.append({'name':'Budget', 'datasets': budget_datasets})
        
        latest_research = Research.query.filter_by(country_id=country.id).order_by(desc(Research.saved_date)).paginate(1, 1, False).items
        research = Research.query.filter_by(country_id=country.id).order_by(desc(Research.saved_date))
        staff = Staff.query.filter_by(country_id=country.id).order_by(Staff.sort_order)
        #url = countryimages.url(country.filename) if country.filename else None
        url = app.config['S3_URL'] + 'countryimages/' + country.filename if country.filename else None
        
        #codebookurl = codebookfiles.url(country.codebookfilename) if country.codebookfilename else None
        codebookurl = app.config['S3_URL'] + 'codebookfiles/' + country.codebookfilename if country.codebookfilename else None
        
        
        return render_template("country.html",
                               countries=countries,
                               pane=pane,
                               url=url,
                               codebookurl = codebookurl,
                               latest_research=latest_research,
                               country=country,
                               research=research,
                               staff=staff,
                               categories=cats)
    else:
        abort(404)

@app.route('/<slug>/research/<id>')
def research_item(slug,id):
    countries = Country.query.order_by(Country.name)
    country = Country.query.filter_by(slug=slug).first()
    if country:
        research = Research.query.filter_by(id=id).first()
        return render_template("research_item.html",countries=countries,country=country,research=research)
    else:
        abort(404)

def instances_get_where(db,dataset,sub,topic,frm,to):
    
    # get cursor
    cur = db.session.connection().connection.cursor()
    
    # GET FILTERS
    
    sql = """
    select filters from dataset WHERE dataset.id = %s
    """
    cur.execute(sql,[dataset])
    r = cur.fetchone()
    filters = r[0] if r[0] != None else []
    
    filter_predicates = []
    for filter in filters:
        filterval = request.args.get(filter)
        if (filterval != None):
            filter_predicates.append("datarow->>'" + filter + "'='" + filterval + "'")
      
    # CONSTRUCT WHERE CLAUSE
            
    topic_col = 'subtopic' if sub else 'majortopic'
    sql = " WHERE datarow->>'""" + topic_col + "' = '" + topic + "'"
    if len(filter_predicates) > 0:
        for pred in filter_predicates:
            sql = sql + " AND " + pred
    sql = sql + " AND datarow->>'year' >= '" + frm + "' AND datarow->>'year' <= '" + to + "'"
       
    return sql


def update_stats(db,dataset_id,country_id):

    # get cursor
    cur = db.session.connection().connection.cursor()
    
    # update stats for this dataset
    sql = """
    UPDATE dataset SET stats_year_from =
    (
    SELECT MIN(datarow->>'year')::int
        from (
        select jsonb_array_elements(content)
        from dataset WHERE dataset.id = %s
        ) s(datarow)
        WHERE datarow->>'year' ~ '^[0-9]'
        AND datarow->>'year' != '0'
    ),
    stats_year_to = (
    SELECT MAX(datarow->>'year')::int
        from (
        select jsonb_array_elements(content)
        from dataset WHERE dataset.id = %s
        ) s(datarow)
        WHERE datarow->>'year' ~ '^[0-9]'
        AND datarow->>'year' != '0'
    ),
    stats_observations = (
    SELECT COUNT(datarow->'id')::int
        from (
        select jsonb_array_elements(content)
        from dataset WHERE dataset.id = %s
        ) s(datarow)
        WHERE datarow->>'year' ~ '^[0-9]'
        AND datarow->>'year' != '0'
    )
    WHERE id = %s
    """   
    cur.execute(sql,[dataset_id,dataset_id,dataset_id,dataset_id])

    # update stats for the whole country
    sql = """
    UPDATE country SET 
    stats_series = (SELECT COUNT(id) FROM dataset WHERE ready=true AND country_id=%s),
    stats_year_from = (SELECT MIN(stats_year_from) FROM dataset WHERE ready=true AND country_id=%s),
    stats_year_to = (SELECT MAX(stats_year_to) FROM dataset WHERE ready=true AND country_id=%s),
    stats_observations = (SELECT SUM(stats_observations) FROM dataset WHERE ready=true AND country_id=%s) 
    WHERE id = %s
    """
    cur.execute(sql,[country_id,country_id,country_id,country_id,country_id])
    db.session.commit() 

def convert_to_utf8(filename):
    # gather the encodings you think that the file may be
    # encoded inside a tuple
    encodings = ('utf-8','macintosh','windows-1250','iso-8859-1','iso-8859-2','utf-16','utf-7','ibm852','shift_jis','iso-2022-jp')
 
    # try to open the file and exit if some IOError occurs
    try:
        f = open(filename, 'r').read()
    except Exception:
        return False
        #sys.exit(1)
 
    # now start iterating in our encodings tuple and try to
    # decode the file
    for enc in encodings:
        try:
            # try to decode the file with the first encoding
            # from the tuple.
            # if it succeeds then it will reach break, so we
            # will be out of the loop (something we want on
            # success).
            # the data variable will hold our decoded text
            data = f.decode(enc)
            break
        except Exception:
            # if the first encoding fail, then with the continue
            # keyword will start again with the second encoding
            # from the tuple an so on.... until it succeeds.
            # if for some reason it reaches the last encoding of
            # our tuple without success, then exit the program.
            if enc == encodings[-1]:
                return False
                #sys.exit(1)
            continue
 
    # now get the absolute path of our filename and append .bak
    # to the end of it (for our backup file)
    #fpath = os.path.abspath(filename)
    #newfilename = fpath + '.bak'
    # and make our backup file with shutil
    #shutil.copy(filename, newfilename)
 
    # and at last convert it to utf-8
    f = open(filename, 'w')
    try:
        f.write(data.encode('utf-8'))
        f.close()
        return True
    except Exception, e:
        f.close()
        return e
