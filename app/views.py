import os
import psycopg2
import urllib
import urllib2
from sqlalchemy import desc
from psycopg2.extras import RealDictCursor
from datetime import datetime
from functools import wraps, update_wrapper
from flask import render_template, flash, redirect, url_for, request, make_response, send_file, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
from json import dumps
from slugify import slugify
from app import app, db, lm, newsimages, countryimages, staffimages, researchfiles, researchimages, adhocfiles, slideimages
from .models import User, News, Country, Research, Staff, Page, File, Slide
from .forms import NewsForm, LoginForm, CountryForm, UserForm, ResearchForm, StaffForm, PageForm, FileForm, SlideForm
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

######### PUBLIC ROUTES

@app.route('/')
@app.route('/index')
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

@app.route('/test')
def test():
    url = 'http://export.highcharts.com'
    values = {'options':'{"colors":["#7cb5ec","#90ed7d","#f7a35c","#8085e9","#f15c80","#e4d354","#8085e8","#8d4653","#91e8e1"],"symbols":["circle","diamond","square","triangle","triangle-down"],"lang":{"loading":"Loading...","months":["January","February","March","April","May","June","July","August","September","October","November","December"],"shortMonths":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],"weekdays":["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"decimalPoint":".","numericSymbols":["k","M","G","T","P","E"],"resetZoom":"Reset zoom","resetZoomTitle":"Reset zoom level 1:1","thousandsSep":",","printChart":"Print chart","downloadPNG":"Download PNG image","downloadJPEG":"Download JPEG image","downloadPDF":"Download PDF document","downloadSVG":"Download SVG vector image","contextButtonTitle":"Chart context menu"},"global":{"useUTC":true,"canvasToolsURL":"http://code.highcharts.com/4.0.4/modules/canvas-tools.js","VMLRadialGradientURL":"http://code.highcharts.com/4.0.4/gfx/vml-radial-gradient.png"},"chart":{"borderColor":"#4572A7","borderRadius":0,"defaultSeriesType":"line","ignoreHiddenSeries":false,"spacing":[10,10,15,10],"backgroundColor":"#FFFFFF","plotBorderColor":"#C0C0C0","resetZoomButton":{"theme":{"zIndex":20},"position":{"align":"right","x":-10,"y":10}},"renderTo":"chart"},"title":{"text":"","align":"center","margin":15,"style":{"color":"#333333","fontSize":"18px"}},"subtitle":{"text":"","align":"center","style":{"color":"#555555"}},"plotOptions":{"line":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":{"lineWidth":0,"radius":4,"lineColor":"#FFFFFF","states":{"hover":{"enabled":true,"lineWidthPlus":1,"radiusPlus":2},"select":{"fillColor":"#FFFFFF","lineColor":"#000000","lineWidth":2}}},"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":0,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":"center","verticalAlign":"bottom"},"cropThreshold":300,"pointRange":0,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":{"size":10,"opacity":0.25}},"select":{"marker":{}}},"stickyTracking":true,"turboThreshold":1000},"area":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":{"lineWidth":0,"radius":4,"lineColor":"#FFFFFF","states":{"hover":{"enabled":true,"lineWidthPlus":1,"radiusPlus":2},"select":{"fillColor":"#FFFFFF","lineColor":"#000000","lineWidth":2}}},"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":0,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":"center","verticalAlign":"bottom"},"cropThreshold":300,"pointRange":0,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":{"size":10,"opacity":0.25}},"select":{"marker":{}}},"stickyTracking":true,"turboThreshold":1000,"threshold":0},"spline":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":{"lineWidth":0,"radius":4,"lineColor":"#FFFFFF","states":{"hover":{"enabled":true,"lineWidthPlus":1,"radiusPlus":2},"select":{"fillColor":"#FFFFFF","lineColor":"#000000","lineWidth":2}}},"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":0,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":"center","verticalAlign":"bottom"},"cropThreshold":300,"pointRange":0,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":{"size":10,"opacity":0.25}},"select":{"marker":{}}},"stickyTracking":true,"turboThreshold":1000},"areaspline":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":{"lineWidth":0,"radius":4,"lineColor":"#FFFFFF","states":{"hover":{"enabled":true,"lineWidthPlus":1,"radiusPlus":2},"select":{"fillColor":"#FFFFFF","lineColor":"#000000","lineWidth":2}}},"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":0,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":"center","verticalAlign":"bottom"},"cropThreshold":300,"pointRange":0,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":{"size":10,"opacity":0.25}},"select":{"marker":{}}},"stickyTracking":true,"turboThreshold":1000,"threshold":0},"column":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":null,"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":null,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":null,"verticalAlign":null},"cropThreshold":50,"pointRange":null,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":false,"brightness":0.1,"shadow":false},"select":{"marker":{},"color":"#C0C0C0","borderColor":"#000000","shadow":false}},"stickyTracking":false,"turboThreshold":1000,"borderColor":"#FFFFFF","borderRadius":0,"groupPadding":0.2,"pointPadding":0.1,"minPointLength":0,"tooltip":{"distance":6},"threshold":0,"borderWidth":0.2},"bar":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":null,"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":null,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":null,"verticalAlign":null},"cropThreshold":50,"pointRange":null,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":false,"brightness":0.1,"shadow":false},"select":{"marker":{},"color":"#C0C0C0","borderColor":"#000000","shadow":false}},"stickyTracking":false,"turboThreshold":1000,"borderColor":"#FFFFFF","borderRadius":0,"groupPadding":0.2,"pointPadding":0.1,"minPointLength":0,"tooltip":{"distance":6},"threshold":0},"scatter":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":0,"marker":{"lineWidth":0,"radius":4,"lineColor":"#FFFFFF","states":{"hover":{"enabled":true,"lineWidthPlus":1,"radiusPlus":2},"select":{"fillColor":"#FFFFFF","lineColor":"#000000","lineWidth":2}}},"point":{"events":{}},"dataLabels":{"enabled":false,"x":0,"y":0,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":"center","verticalAlign":"bottom"},"cropThreshold":300,"pointRange":0,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":{"size":10,"opacity":0.25}},"select":{"marker":{}}},"stickyTracking":false,"turboThreshold":1000,"tooltip":{"headerFormat":"<span style=\"color:{series.color}\"></span> <span style=\"font-size: 10px;\"> {series.name}</span><br/>","pointFormat":"x: <b>{point.x}</b><br/>y: <b>{point.y}</b><br/>"}},"pie":{"allowPointSelect":false,"showCheckbox":false,"animation":{"duration":1000},"events":{},"lineWidth":2,"marker":null,"point":{"events":{}},"dataLabels":{"enabled":true,"x":0,"y":0,"style":{"color":"#606060","cursor":"default","fontSize":"11px"},"align":"center","verticalAlign":"bottom","distance":30},"cropThreshold":300,"pointRange":0,"states":{"hover":{"lineWidthPlus":1,"marker":{},"halo":{"size":10,"opacity":0.25},"brightness":0.1,"shadow":false},"select":{"marker":{}}},"stickyTracking":false,"turboThreshold":1000,"borderColor":"#FFFFFF","borderWidth":1,"center":[null,null],"clip":false,"colorByPoint":true,"ignoreHiddenPoint":true,"legendType":"point","size":null,"showInLegend":false,"slicedOffset":10,"tooltip":{"followPointer":true}},"series":{"point":{"events":{}},"states":{"hover":{"halo":false}},"shadow":false,"animation":false,"cursor":"pointer"}},"labels":{"style":{"position":"absolute","color":"#3E576F"}},"legend":{"enabled":false,"align":"center","layout":"horizontal","borderColor":"#909090","borderRadius":0,"navigation":{"activeColor":"#274b6d","inactiveColor":"#CCC"},"shadow":false,"itemStyle":{"color":"#333333","fontSize":"12px","fontWeight":"bold","cursor":"pointer"},"itemHoverStyle":{"color":"#000"},"itemHiddenStyle":{"color":"#CCC"},"itemCheckboxStyle":{"position":"absolute","width":"13px","height":"13px"},"symbolPadding":5,"verticalAlign":"bottom","x":0,"y":0,"title":{"style":{"fontWeight":"bold"}}},"loading":{"labelStyle":{"fontWeight":"bold","position":"relative","top":"45%"},"style":{"position":"absolute","backgroundColor":"white","opacity":0.5,"textAlign":"center"}},"tooltip":{"enabled":false,"animation":true,"backgroundColor":"rgba(249, 249, 249, .85)","borderWidth":1,"borderRadius":3,"dateTimeLabelFormats":{"millisecond":"%A, %b %e, %H:%M:%S.%L","second":"%A, %b %e, %H:%M:%S","minute":"%A, %b %e, %H:%M","hour":"%A, %b %e, %H:%M","day":"%A, %b %e, %Y","week":"Week from %A, %b %e, %Y","month":"%B %Y","year":"%Y"},"headerFormat":"<span style=\"font-size: 10px\">{point.key}</span><br/>","pointFormat":"<span style=\"color:{series.color}\"></span> {series.name}: <b>{point.y}</b><br/>","shadow":true,"snap":10,"style":{"color":"#333333","cursor":"default","fontSize":"12px","padding":"8px","whiteSpace":"nowrap"}},"credits":{"enabled":false,"text":"Highcharts.com","href":"http://www.highcharts.com","position":{"align":"right","x":-10,"verticalAlign":"bottom","y":-5},"style":{"cursor":"pointer","color":"#909090","fontSize":"9px"}},"navigation":{"menuStyle":{"border":"1px solid #A0A0A0","background":"#FFFFFF","padding":"5px 0"},"menuItemStyle":{"padding":"0 10px","background":"none","color":"#303030","fontSize":"11px"},"menuItemHoverStyle":{"background":"#4572A5","color":"#FFFFFF"},"buttonOptions":{"symbolFill":"#E0E0E0","symbolSize":14,"symbolStroke":"#666","symbolStrokeWidth":3,"symbolX":12.5,"symbolY":10.5,"align":"right","buttonSpacing":3,"height":22,"theme":{"fill":"white","stroke":"none"},"verticalAlign":"top","width":24}},"exporting":{"type":"image/png","url":"http://export.highcharts.com/","buttons":{"contextButton":{"menuClassName":"highcharts-contextmenu","symbol":"menu","_titleKey":"contextButtonTitle","menuItems":[{"textKey":"printChart"},{"separator":true},{"textKey":"downloadPNG"},{"textKey":"downloadJPEG"},{"textKey":"downloadPDF"},{"textKey":"downloadSVG"}]}}},"xAxis":[{"title":{"text":"Year"},"categories":["2001","2002","2003","2004","2005","2006","2007","2008","2009","2010"],"index":0,"isX":true}],"yAxis":[{"title":{"text":"Count"},"plotLines":[{"value":0,"width":1,"color":"#808080"}],"index":0}],"series":[{"name":"United States: NYT #Gender","data":[0,1,5,5,3,2,0,10,9,8],"_colorIndex":0,"_symbolIndex":0}]}','type':'image/png'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return the_page

@app.route('/countries/<slug>')
@app.route('/countries/<slug>/<pane>')
def country(slug,pane='about'):
    countries = Country.query.order_by(Country.name)
    country = Country.query.filter_by(slug=slug).first()
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
                           staff=staff)

@app.route('/countries/<slug>/research/<id>')
def research_item(slug,id):
    countries = Country.query.order_by(Country.name)
    country = Country.query.filter_by(slug=slug).first()
    research = Research.query.filter_by(id=id).first()
    return render_template("research_item.html",countries=countries,country=country,research=research) 
    

@app.route('/tool')
def tool():
    return render_template('tool.html')

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



## COUNTRIES

@app.route('/admin/countries')
@login_required
def admin_country_list():
    countries = Country.query.order_by(Country.name)
    return render_template('admin/country_list.html',
                           countries=countries)
                                               
@app.route('/admin/countries/<slug>', methods=['GET', 'POST'])
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
 

@app.route('/admin/countries/delete/<id>')
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

@app.route('/admin/countries/removeimage/<id>')
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

@app.route('/admin/countries/<slug>/news')
@app.route('/admin/countries/<slug>/news/p/<int:page>')
@login_required
def admin_news_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    news = News.query.filter_by(country_id=country.id).order_by(desc(News.saved_date)).paginate(page, 10, False)
    #news = News.query.all()
    return render_template('admin/news_list.html',
                           country=country,
                           news=news)
                    
@app.route('/admin/countries/<slug>/news/<id>', methods=['GET', 'POST'])
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

@app.route('/admin/countries/<slug>/news/delete/<id>')
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

@app.route('/admin/countries/<slug>/news/removeimage/<id>')
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



@app.route('/admin/countries/<slug>/research')
@app.route('/admin/countries/<slug>/research/p/<int:page>')
@login_required
def admin_research_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    research = Research.query.filter_by(country_id=country.id).order_by(desc(Research.saved_date)).paginate(page, 10, False)
    return render_template('admin/research_list.html', 
                           country=country,
                           research=research)

@app.route('/admin/countries/<slug>/research/<id>', methods=['GET', 'POST'])
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

@app.route('/admin/countries/<slug>/research/delete/<id>')
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

@app.route('/admin/countries/<slug>/research/removefile/<id>')
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

@app.route('/admin/countries/<slug>/research/removeimage/<id>')
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
@app.route('/admin/countries/<slug>/staff')
@app.route('/admin/countries/<slug>/staff/p/<int:page>')
@login_required
def admin_staff_list(slug,page=1):
    country = Country.query.filter_by(slug=slug).first()
    staff = Staff.query.filter_by(country_id=country.id).order_by(Staff.sort_order).paginate(page, 10, False)
    return render_template('admin/staff_list.html', 
                           country=country,
                           staff=staff)

@app.route('/admin/countries/<slug>/staff/<id>', methods=['GET', 'POST'])
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

@app.route('/admin/countries/<slug>/staff/delete/<id>')
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

@app.route('/admin/countries/<slug>/staff/removeimage/<id>')
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