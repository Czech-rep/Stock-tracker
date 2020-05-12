from flask import render_template, request, redirect, url_for
from sqlalchemy import exc
from flask_login import login_required

from main import app
from database import db, StocksItems
from bankier_scr import price_extracter_conv, ScrappingFailed
from loging import login_manager

@app.route('/') # route decorator should be outermost - but why?
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
            return render_template('error_page.html', error_message=f"invalid count of asset: '{count}' is not a number", url_back='/')
        try:
            results = price_extracter_conv(symbol)
        except ScrappingFailed as e:                         
            return render_template('error_page.html', error_message=e, url_back='/')

        new_item = StocksItems(symbol=symbol, count=count)
        try:
            db.session.add(new_item)        
            save_prices(new_item, results)
            new_item.starting_price = new_item.last_price
            db.session.commit()
        except NameError:
            return render_template('error_page.html', error_message='issue adding item', url_back='/')
        except exc.IntegrityError:
            return render_template('error_page.html', error_message=f'price of {symbol} is already tracked!', url_back='/')
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete_item(id):
    item_to_delete = StocksItems.query.get_or_404(id)
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
    except:
        return render_template('error_page.html', error_message='deletion unsuccessfull', url_back='/')
    return redirect('/')

@app.route('/refresh/')
@login_required
def refresh():      #funkcja pobiejaraca dane z sieci i wstawiajaca do bazy danych
    for item in StocksItems.query.all():
        save_prices(item, price_extracter_conv(item.symbol))
    try:
        db.session.commit()
    except:
        return render_template('error_page.html', error_message='not succeded refreshing', url_back='/')
    return redirect('/')

def save_prices(item, results):                             
    if results is not None: 
        try:                                                    
            item.last_price, item.change_rel, item.change_absolute = results  # here out web scrapper is used
        except:
            return render_template('error_page.html', error_message=f'issue occured during updating item {item.symbol}', url_back='/')

@app.route('/modify/<int:id>', methods=['POST', 'GET']) # page for modification of quantity of asset
@login_required
def modify(id):
    item_to_modify = StocksItems.query.get_or_404(id)
    if request.method == 'POST':
        count = request.form['new_count']
        try:
            count = int(count)
        except ValueError:
            return render_template('error_page.html', error_message=f"invalid count of asset: '{count}' is not a number", url_back=f'/modify/{id}')
        item_to_modify.count = count
        try:
            db.session.commit()
        except:
            return render_template('error_page.html', error_message=f'issue occured during updating item {item.symbol}', url_back='/')
        return redirect('/')

    return render_template('asset_alteration.html', item=item_to_modify)

@app.route('/profile/')
@login_required
def profile():
    items = StocksItems.query.all()   
    S = sum( item.count*item.last_price for item in items )
    print(S)

    return render_template('profile.html', total_wallet=S)