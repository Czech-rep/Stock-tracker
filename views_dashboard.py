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
        
        # lets check symbol
        asset_id = None
        is_it_in = StockData.query.filter_by(symbol=symbol).first()
        if is_it_in is not None:                                                    # so this asset is already tracked # we could refresh
            asset_id = is_it_in.id
            if UserItems.query.filter_by(user_id=current_user.id, asset_id=asset_id).first():   # does this user have this item ?
                return render_template('error_page.html', error_message=f'price of {symbol} is already tracked! Use modify to change quantity', url_back='/')
        else:
            try:
                new_asset = StockData(symbol=symbol)
                save_prices(new_asset)                       # update or save of prices # exception is handled inside
                db.session.add(new_asset) 
                db.session.commit()                         # i have to add to db to have asset_id
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
    item_to_delete = UserItems.query.get_or_404(id)
    try:
        db.session.delete(item_to_delete)
        db.session.commit()
    except:
        return render_template('error_page.html', error_message='deletion unsuccessfull', url_back='/')
    clean_db() # function cleanes untracked items
    return redirect('/')

def clean_db(): # function deletes stocks items that are not tracked by any user
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f''' 
    delete from stock_data where id not in (
        select asset_id 
        from user_items 
        group by asset_id
    );''')
    # c.execute('delete from stock_data where symbol like "11%"; ') # for testing
    conn.commit()
    print(6)

@app.route('/refresh/')
@login_required
def refresh():      # for now, it will update all tracked assets, no matter by who
    try:
        for item in StockData.query.all():
            save_prices(item)
        db.session.commit()
    except ScrappingFailed as e:
        return render_template('error_page.html', error_message=e, url_back='/')
    except:
        return render_template('error_page.html', error_message='not succeded refreshing', url_back='/')
    return redirect('/')

def save_prices(item):    # takes object of StockCata   # function updates data for one asset    
    item.last_price, item.change_rel, item.change_absolute = price_extracter_conv(item.symbol)   # here out web scrapper is used

@app.route('/modify/<int:id>', methods=['POST', 'GET']) # page for modification of quantity of asset
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
    # items = UserItems.query.all()   
    # S = sum( item.count*item.last_price for item in items )
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

    return render_template('profile.html', wallet_value=S) # current_user doesnt even need to bo provided

