import os
import uuid
import psycopg2
import urllib
import urllib2
import csv
from sqlalchemy import desc
from psycopg2.extras import RealDictCursor
from datetime import datetime
from functools import wraps, update_wrapper
from flask import render_template, flash, redirect, url_for, request, make_response, send_file, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
from json import dump, dumps, loads
from slugify import slugify
from app import app, db, lm, newsimages, countryimages, staffimages, researchfiles, researchimages, adhocfiles, slideimages, codebookfiles, datasetfiles
from .models import User, News, Country, Research, Staff, Page, File, Slide, Chart, Dataset, Category
from .forms import NewsForm, LoginForm, CountryForm, UserForm, ResearchForm, StaffForm, PageForm, FileForm, SlideForm, DatasetForm
from datetime import datetime

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
    resp=make_response(render_template('tool.html',user=user,slug=slug,options=options,recent=recent,projectid=projectid))    
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
        values['options'] = dumps(loads(exists.options))
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


######### CMS ROUTES

@app.route('/')
def index():
    slides = Slide.query.filter_by(active=True).paginate(1,3,False).items
    for item in slides:
        if item.imagename:
            url = slideimages.url(item.imagename)
            item.url = url
    news = News.query.order_by(desc(News.saved_date)).paginate(1, 2, False).items
    for item in news:
        if item.filename:
            url = newsimages.url(item.filename)
            item.url = url
    countries = Country.query.order_by(Country.name)
    return render_template("index.html",
                           countries=countries,
                           slides=slides,
                           news=news)

@app.route('/news')
@app.route('/news/<int:page>')
def news(page=1):
    countries = Country.query.order_by(Country.name)
    news = News.query.order_by(desc(News.saved_date)).paginate(page, 3, False)
    for item in news.items:
        if item.filename:
            url = newsimages.url(item.filename)
            item.url = url
    return render_template('news.html',news=news,countries=countries)

@app.route('/news/<slug>')
def news_item(slug):    
    item = News.query.filter_by(slug=slug).first()
    if item.filename:
            url = newsimages.url(item.filename)
            item.url = url
    news = News.query.filter(News.slug!=slug).order_by(desc(News.saved_date)).limit(3).all()
    return render_template('news_item.html',item=item,news=news)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/datasets_codebooks')
def datasets_codebooks():
    return render_template('datasets_codebooks.html')

@app.route('/pages/<slug>')
def page(slug):
    countries = Country.query.order_by(Country.name)
    page = Page.query.filter_by(slug=slug).first()
    return render_template('page.html',page=page,countries=countries)

@app.route('/files/<slug>')
@nocache
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
        page.slug = slugify(page.title)
        if slug == 'add':
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
            file.filename = filename
        file.name = form.name.data
        file.slug = slugify(file.name)
        if slug == 'add':
            db.session.add(file)
        db.session.commit()
    	flash('File "%s" saved' %
              (form.name.data))
        return redirect( 'admin/files' )
    else:
        url = adhocfiles.url(file.filename) if file.filename else None
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
        path = adhocfiles.path(file.filename)
        if os.path.isfile(path):
            os.remove(path)
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
        url = slideimages.url(slide.imagename) if slide.imagename else None
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
        path = slideimages.path(slide.imagename)
        if os.path.isfile(path):
            os.remove(path)
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
@login_required
def admin_country_item(slug):
    country = Country() if slug == 'add' else Country.query.filter_by(slug=slug).first()
    form = CountryForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = countryimages.save(request.files['image'])
            country.filename = filename
        country.name = form.name.data
        country.short_name = form.short_name.data
        country.principal = form.principal.data
        country.location = form.location.data
        country.heading = form.heading.data
        country.about = form.about.data
        country.embed_url = form.embed_url.data
        country.slug = slugify(country.short_name)
        if slug == 'add':
            db.session.add(country)
        db.session.commit()
    	flash('Country "%s" saved' %
              (form.name.data))
        return redirect( url_for('admin_country_item',slug=current_user.country.slug) if current_user.country else 'admin/countries' )
    else:
        url = countryimages.url(country.filename) if country.filename else None
        if request.method == 'GET':
            form.name.data = country.name
            form.short_name.data = country.short_name
            form.principal.data = country.principal
            form.location.data = country.location
            form.heading.data = country.heading
            form.about.data = country.about
            form.embed_url.data = country.embed_url
    
    return render_template('admin/country_item.html', 
                           id=country.id,
                           slug=country.slug,
                           url=url,
                           form=form)
 

@app.route('/admin/projects/delete/<id>')
@login_required
def admin_country_delete(id):
    country = Country.query.filter_by(id=id).first()
    if country is not None:
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
        path = countryimages.path(country.filename)
        if os.path.isfile(path):
            os.remove(path)
        country.filename = None
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
                    
@app.route('/admin/projects/<slug>/news/<id>', methods=['GET', 'POST'])
@login_required
def admin_news_item(slug,id):
    country = Country.query.filter_by(slug=slug).first()
    news = News() if id == 'add' else News.query.filter_by(id=id).first()
    form = NewsForm()
    if form.validate_on_submit():
        if 'image' in request.files and request.files['image'].filename != '':
            filename = newsimages.save(request.files['image'])
            news.filename = filename
        news.title = form.title.data
        news.content = form.content.data
        news.slug = slugify(news.title)
        if id == 'add':
            news.country_id = country.id
            db.session.add(news)
        news.saved_date = datetime.utcnow()
        db.session.commit()
    	flash('News item "%s" saved' %
              (form.title.data))
        return redirect(url_for('admin_news_list',slug=slug))
    else:
        url = newsimages.url(news.filename) if news.filename else None
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
        path = newsimages.path(news.filename)
        if os.path.isfile(path):
            os.remove(path)
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
            research.filename = filename
        if 'image' in request.files and request.files['image'].filename != '':
            imagename = researchimages.save(request.files['image'])
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
        fileurl = researchfiles.url(research.filename) if research.filename else None
        imageurl = researchimages.url(research.imagename) if research.imagename else None
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
        path = researchfiles.path(research.filename)
        if os.path.isfile(path):
            os.remove(path)
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
        path = researchimages.path(research.imagename)
        if os.path.isfile(path):
            os.remove(path)
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
        url = staffimages.url(staff.filename) if staff.filename else None
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
        path = staffimages.path(staff.filename)
        if os.path.isfile(path):
            os.remove(path)
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
@app.route('/admin/projects/<slug>/datasets/p/<int:page>')
@login_required
def admin_dataset_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    datasets = Dataset.query.filter_by(country_id=country.id).order_by(desc(Dataset.saved_date)).paginate(page, 10, False)
    return render_template('admin/dataset_list.html',
                           country=country,
                           datasets=datasets)
                    
@app.route('/admin/projects/<slug>/dataset/<id>', methods=['GET', 'POST'])
@login_required
def admin_dataset_item(slug,id):
    country = Country.query.filter_by(slug=slug).first()
    dataset = Dataset() if id == 'add' else Dataset.query.filter_by(id=id).first()
    form = DatasetForm()
    form.fieldnames=[]
    if 'content' in request.files and request.files['content'].filename != '':
            datasetfilename = datasetfiles.save(request.files['content'])
            csvfile = open(datasetfiles.path(datasetfilename), 'rU')
            reader = csv.DictReader(csvfile)
            reader.fieldnames = [item.lower() for item in reader.fieldnames]
            form.fieldnames = reader.fieldnames
    if form.validate_on_submit():
        if 'codebook' in request.files and request.files['codebook'].filename != '':
            codebookfilename = codebookfiles.save(request.files['codebook'])
            dataset.codebookfilename = codebookfilename
        if 'content' in request.files and request.files['content'].filename != '':
            filters = []
            for fieldname in reader.fieldnames:
                if fieldname.split('_')[0] == 'filter':
                    #filtername = fieldname[7:].replace("_"," ")
                    filters.append(fieldname)
            dataset.filters = filters
            dataset.datasetfilename = datasetfilename
            thedata = [ row for row in reader ]
            dataset.content = thedata
            dataset.ready = True
            #cur = db.session.connection().connection.cursor()
            #cur.execute("UPDATE dataset SET content=%s",dumps(thedata))
            #db.session.commit() 
        dataset.display = form.display.data
        dataset.short_display = form.short_display.data
        dataset.description = form.description.data
        dataset.unit = form.unit.data
        dataset.source = form.source.data
        dataset.category = form.category.data        
        if id == 'add':
            dataset.country_id = country.id
            db.session.add(dataset)
        dataset.saved_date = datetime.utcnow()
        db.session.commit()
    	flash('Dataset "%s" saved' %
              (form.display.data))
        return redirect(url_for('admin_dataset_list',slug=slug))
    else:
        dataseturl= datasetfiles.url(dataset.datasetfilename) if dataset.datasetfilename else None
        codebookurl = codebookfiles.url(dataset.codebookfilename) if dataset.codebookfilename else None
        url = None
        if request.method == 'GET':
            form.display.data = dataset.display
            form.short_display.data = dataset.short_display
            form.description.data = dataset.description
            form.unit.data = dataset.unit
            form.source.data = dataset.source
            form.category.data = dataset.category
    
    return render_template('admin/dataset_item.html', 
                           id=dataset.id,
                           country=country,
                           slug=slug,
                           ready=dataset.ready,
                           dataseturl=dataseturl,
                           datasetfilename=dataset.datasetfilename,
                           codebookurl=codebookurl,
                           codebookfilename=dataset.codebookfilename,
                           form=form)

@app.route('/admin/projects/<slug>/dataset/delete/<id>')
@login_required
def admin_dataset_delete(slug,id):
    dataset = Dataset.query.filter_by(id=id).first()
    if dataset is not None:
        title = dataset.display
        db.session.delete(dataset)
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
        #dataset.filename = None
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
        path = codebookfiles.path(dataset.codebookfilename)
        if os.path.isfile(path):
            os.remove(path)
        dataset.codebookfilename = None
        db.session.commit()
        return redirect(url_for('admin_dataset_item',slug=slug,id=id))
    flash('Dataset not found!')
    return redirect(url_for('admin'))
    

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
    cur.execute("""SELECT DISTINCT(c.*) FROM country c INNER JOIN dataset d ON c.id = d.country_id ORDER BY c.name""")
    #cur.execute("""SELECT * FROM country ORDER BY name""")
    return dumps(cur.fetchall())

@app.route('/api/categories')
def api_categories():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    #cur.execute("""SELECT DISTINCT(c.*) FROM category c INNER JOIN dataset d ON c.id = d.category_id ORDER BY c.name""")
    cur.execute("""SELECT c.id as category_id, c.* FROM category c ORDER BY c.name""")
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
           JOIN subtopicz t 
             ON m.majortopic = t.majortopic 
    GROUP  BY m.id,
	      m.shortname,
              m.majortopic 
    ORDER  BY m.id
    """)
    return dumps(cur.fetchall())

@app.route('/api/datasets')
def api_datasets():
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    #cur.execute("""SELECT category, short_display as name FROM datasets WHERE controller IS NOT NULL ORDER BY short_display""")
    cur.execute("""SELECT d.id, d.category_id AS category, d.short_display as name, c.short_name as country, d.filters as filters FROM dataset d INNER join country c ON d.country_id = c.id WHERE d.ready=true ORDER BY d.short_display""")
    return dumps(cur.fetchall())

@app.route('/api/instances/<dataset>/<topic>/<year>')
def api_instances(dataset,topic,year):
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    data = {}
    
    # GET FILTERS
    
    sql = """
    select filters from dataset WHERE dataset.id = %s
    """
    cur.execute(sql,[dataset])
    r = cur.fetchone()
    filters = loads(r["filters"]) if r["filters"] != None else []
    
    filter_predicates = []
    for filter in filters:
        filterval = request.args.get(filter)
        if (filterval != None):
            filter_predicates.append("datarow->>'" + filter + "'='" + filterval + "'")
    
    topic_col = 'majortopic' if int(topic) < 100 else 'subtopic'
    
    # INSTANCES
    
    sql = """
    select datarow->>'source' as source, datarow->>'description' as description
    from (
      select json_array_elements(content)
      from dataset WHERE dataset.id = %s
    ) s(datarow)
    where datarow->>'""" + topic_col + "' = %s AND datarow->>'year' = %s"
    
    if len(filter_predicates) > 0:
        for pred in filter_predicates:
            sql = sql + " AND " + pred
    
    #app.logger.debug(sql)
    cur.execute(sql,[dataset,topic,year])
    return dumps(cur.fetchall())
    
@app.route('/api/measures/dataset/<dataset>/topic/<topic>')
def api_measures(dataset,topic):
    
    # CHECK CACHE
    cached_path = '/var/www/cap/datacache/' + dataset + '-' + topic + request.query_string + '-measures.json'
    app.logger.debug(cached_path);
    
    if (os.path.isfile(cached_path)):
        return send_file(cached_path)
    
    # NO CACHE, GO TO THE DB!!
    
    conn = psycopg2.connect(app.config['CONN_STRING'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    data = {}
    
    # GET FILTERS
    
    sql = """
    select filters from dataset WHERE dataset.id = %s
    """
    cur.execute(sql,[dataset])
    r = cur.fetchone()
    filters = loads(r["filters"]) if r["filters"] != None else []
    
    filter_predicates = []
    for filter in filters:
        filterval = request.args.get(filter)
        if (filterval != None):
            filter_predicates.append("datarow->>'" + filter + "'='" + filterval + "'")
    
    topic_col = 'majortopic' if int(topic) < 100 else 'subtopic'
    
    # COUNT
    
    sql = """
    SELECT yc.year::int, yc.cnt::int FROM (
    select datarow->>'year' AS year, COUNT(datarow->'id') as cnt
    from (
    select json_array_elements(content)
    from dataset WHERE dataset.id = %s
    ) s(datarow)
    where datarow->>'""" + topic_col + "' = %s"
    
    if len(filter_predicates) > 0:
        for pred in filter_predicates:
            sql = sql + " AND " + pred 
            
    sql = sql + """
    GROUP BY year) AS yc ORDER by year
    """
   
    #app.logger.debug(sql)
    
    cur.execute(sql,[dataset,topic])
    d = cur.fetchall()
    count = []
    for i in range(1946,2016):
        found = False
        for r in d:
            if (r["year"] == i):
                count.append(r["cnt"])
                found = True
        if (found == False):
            count.append(0)
    data['count'] = count 
    
    
    # PERCENT CHANGE
    percent_change = [None]
    i = 0
    for c in count:
        i += 1
        if i < len(count):
            pc = float(count[i] - count[i - 1])/count[i - 1] if (count[i - 1] > 0) else None
            if pc:
                percent_change.append(int(100 * float("{0:.2f}".format(pc))))
            else:
                percent_change.append(None)
    data['percent_change'] = percent_change
    #app.logger.debug(len(count))
    
    # PERCENT TOTAL
    sql = """
    SELECT yt.year::int, yt.total::int FROM (
    select datarow->>'year' AS year, COUNT(datarow->'id') as total
    from (
      select json_array_elements(content)
      from dataset WHERE dataset.id = %s
    ) s(datarow)
    WHERE 1=1"""
    
    if len(filter_predicates) > 0:
        for pred in filter_predicates:
            sql = sql + " AND " + pred 
    
    sql = sql + """
    GROUP BY year) AS yt ORDER by year
    """
    cur.execute(sql,[dataset])
    d = cur.fetchall()
    percent_total = []
    for i in range(1946,2016):
        found = False
        for r in d:
            if (r["year"] == i):
                pt = float(count[i - 1946])/r["total"]
                percent_total.append(int(100 * float("{0:.2f}".format(pt))))
                found = True
        if (found == False):
            percent_total.append(0)     
    data['percent_total'] = percent_total
    
    # WRITE CACHE
    with open(cached_path, 'w') as outfile:
        dump(data, outfile)
         
    return dumps(data)
    #return dumps(cur.fetchall())

    
@app.route('/<slug>')
@app.route('/<slug>/<pane>')
def country(slug,pane='about'):
    country = Country.query.filter_by(slug=slug).first()
    if country:
        countries = Country.query.filter(Country.id != country.id).order_by(Country.name).all()
        categories = Category.query.order_by(Category.name).all()
        cats = []
        for category in categories:
            datasets = [u.__dict__ for u in Dataset.query.filter_by(country_id=country.id).filter_by(category_id=category.id).filter_by(ready=True).all()]
            app.logger.debug(datasets)
            if len(datasets) > 0:
                setattr(category, 'datasets', datasets)
                cats.append(category)
        #categories = [{"name":"Good Datasets","datasets":datasets},{"name":"Bad Datasets","datasets":datasets}]
        latest_research = Research.query.filter_by(country_id=country.id).order_by(desc(Research.saved_date)).paginate(1, 1, False).items
        research = Research.query.filter_by(country_id=country.id).order_by(desc(Research.saved_date))
        staff = Staff.query.filter_by(country_id=country.id).order_by(Staff.sort_order)
        url = countryimages.url(country.filename) if country.filename else None
        return render_template("country.html",
                               countries=countries,
                               pane=pane,
                               url = url,
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