from flask import render_template, request, redirect, url_for
from sqlalchemy import exc
from flask_login import login_required
import sqlite3

from main import app
from database import db, UserItems, StockData
from bankier_scr import price_extracter_conv, ScrappingFailed
from views_loging import login_manager, current_user


def dict_factory(cursor, row): # this is to overwrite row_factory and make queries return dictinaries instead of tuples
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('database.db')
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute(f''' 
    select stock_data.symbol symbol, user_items.count count 
    ,stock_data.last_price price
    ,stock_data.change_rel change_rel, stock_data.change_absolute change_absolute
    ,stock_data.last_price*user_items.count value
    ,user_items.id id
    from user_items 
    left join stock_data on user_items.asset_id=stock_data.id 
    where user_items.user_id={current_user.id}
    ''')
    items = c.fetchall()
    return render_template('startpage.html', items=items)

@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    if request.method == 'POST':
        symbol, count = request.form['stock_symbol'], request.form['count']   
        try:
            count = int(count)
        except ValueError:
            return render_template('error_page.html', error_message=f"invalid count of asset: '{count}' is not a number", url_back='/')
        
        asset_id = None # lets check symbol
        is_it_in = StockData.query.filter_by(symbol=symbol).first()
        if is_it_in is not None:                                                    # so this asset is already tracked # we could refresh
            asset_id = is_it_in.id
            if UserItems.query.filter_by(user_id=current_user.id, asset_id=asset_id).first():   # check if current user have this item
                return render_template('error_page.html', error_message=f'price of {symbol} is already tracked! Use modify to change quantity', url_back='/')
        else:
            try:
                new_asset = StockData(symbol=symbol)
                item.last_price, item.change_rel, item.change_absolute = price_extracter_conv(item.symbol) # scrapping
                db.session.add(new_asset) 
                db.session.commit()                         
            except ScrappingFailed as e:
                return render_template('error_page.html', error_message=e, url_back='/')
        if asset_id is None: asset_id = new_asset.id  
        try:
            new_product = UserItems(user_id=current_user.id, asset_id=asset_id, count=count)
            db.session.add(new_product)
            db.session.commit()
        except NameError:
            return render_template('error_page.html', error_message='issue adding item', url_back='/')
        except exc.IntegrityError:
            return render_template('error_page.html', error_message=f'price of {symbol} is already tracked!', url_back='/')
    return redirect('/')

@app.route('/delete/<int:id>')
@login_required
def delete_item(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f'delete from user_items where id={id}') # we have access to key in table user_items
    c.execute(f'''
    delete from stock_data 
    where id not in (
        select distinct asset_id from user_items
    )
    ''') # could be better efficiency
    conn.commit()
    print(6)
    return redirect('/')

@app.route('/refresh/')
@login_required
def refresh():      # for now, it will update all tracked assets, no matter by who
    try:
        for item in StockData.query.all():    # here out web scrapper is used
            item.last_price, item.change_rel, item.change_absolute = price_extracter_conv(item.symbol)   
        db.session.commit()
    except ScrappingFailed as e:
        return render_template('error_page.html', error_message=e, url_back='/')
    except:
        return render_template('error_page.html', error_message='not succeded refreshing', url_back='/')
    return redirect('/') 

@app.route('/modify/<int:id>', methods=['POST', 'GET']) 
@login_required
def modify(id):
    item_to_modify = UserItems.query.get_or_404(id)
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
            return render_template('error_page.html', error_message=f'issue occured during updating item {item_to_modify.symbol}', url_back='/')
        return redirect('/')

    return render_template('asset_alteration.html', item=item_to_modify)

@app.route('/profile/') # why does order of decorators matter?
@login_required
def profile():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f''' 
    select sum(u.count*d.last_price)
    from user_items u
    left join stock_data d on u.asset_id=d.id
    where u.user_id={current_user.id}
    ''')
    S = c.fetchall()[0][0]
    print(S)

    return render_template('profile.html', wallet_value=S) 

