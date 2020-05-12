from flask import render_template, request, redirect, url_for
from sqlalchemy import exc
from flask_login import login_required

from main import app
from database import db, StocksItems
from price_scrapper import price_extracter_conv
from loging import login_manager

@app.route('/') # route decorator should be outermost - but why?
@app.route('/index/')
@login_required
def index():
    items = StocksItems.query.all()                     # czemu query dotyczy klasy a nie db
    return render_template('startpage.html', items=items) # would u belive that current_user is passed there independently?

@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    if request.method == 'POST': # jak rozumiem zawsze jest metoda post, bo tak to wywuluje. jednak musi byc if 
        symbol, count = request.form['stock_symbol'], request.form['count']     #gets data from page
        try:
            count = int(count)
        except ValueError:
            return render_template('error_page.html', error_message="invalid count of asset", url_back=url_back)
            # error_page("invalid count of asset", url_back='/')
        results = price_extracter_conv(symbol)
        if results is None:                                #checks if symbol is correct
            return render_template('error_page.html', error_message="unknown asset symbol provided")
            return "unknown asset symbol provided. <br/> <a href='/'> back </a>"

        new_item = StocksItems(symbol=symbol, count=count)
        try:
            db.session.add(new_item)        
            save_prices(new_item, results)
            new_item.starting_price = new_item.last_price
            db.session.commit()
        except NameError:
            return render_template('error_page.html', error_message='issue adding item', url_back='/') #'<h3> issue adding item <br/> <a href="/">back</a> </h3>'
        except exc.IntegrityError:
            return render_template('error_page.html', error_message='asset already in database')
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete_item(id):
    item_to_delete = StocksItems.query.get_or_404(id)
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
    except:
        return '<h3> delete not succeded </h3> <a href="/">back</a> '
    return redirect('/')

@app.route('/refresh/')
@login_required
def refresh():      #funkcja pobiejaraca dane z sieci i wstawiajaca do bazy danych
    for item in StocksItems.query.all():
        save_prices(item, price_extracter_conv(item.symbol))
    try:
        db.session.commit()
    except:
        return 'not succeded refreshing'
    return redirect('/')

def save_prices(item, results):                             
    if results is not None: 
        try:                                                    
            item.last_price, item.change_rel, item.change_absolute = results        #gets prices if not error
        except:
            return 'issue updating item {{ item.id }}'

@app.route('/modify/<int:id>', methods=['POST', 'GET']) # Just to enter modify mode
@login_required
def modify(id):
    item_to_modify = StocksItems.query.get_or_404(id)
    if request.method == 'POST':
        count = request.form['new_count']
        try:
            count = int(count)
        except ValueError:
            return "invalid new count provided"
        item_to_modify.count = count
        try:
            db.session.commit()
        except:
            return 'not succeded updating'
        return redirect('/')

    return render_template('asset_alteration.html', item=item_to_modify)

@app.route('/testowa/')
@login_required
def testowa():
    return '<h3>siema</h3>'

# @app.route('/error_page/ms_code/url_back')
# def error_page(error_message='some error occured', url_back='/'):
#     return render_template('error_page.html', error_message="invalid count of asset", url_back=url_back)
