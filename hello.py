from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack, make_response

import cStringIO as cio

import sys

sys.path.insert(1,'/usr/lib/pymodules/python2.7')

import pandas as pd

dw = pd.get_option('display.width')
from trump.orm import SymbolManager

sm = SymbolManager()

from jinja2 import Markup

app = Flask(__name__)

def symurl(sym):
    return Markup(r"<a href=/s/{0}>{0}</a>".format(sym))
app.jinja_env.globals.update(symurl=symurl)

def taglink(tag):
    return Markup(r'<a class="btn btn-xs btn-success" href="/t/{0}">{0}</a>'.format(tag))
app.jinja_env.globals.update(taglink=taglink)
    

@app.route("/about")
def about():
    eng = sm.eng
    mac = "Currently Connected to..."
    info = str(eng.dialect) + Markup( "<br>" + str(eng.name) + "<br>" + str(eng))
    return render_template('about.html', msg_title="About Trump", msg_macro=mac, msg_info=info)

@app.route("/raiseanerror")
def er():
    somedict = {'jeff' : 'wins', 'trump': 'rock'}
    
    print somedict
    
    raise Exception("Nothing , jeff put this here")

@app.route("/chart/<symbol>")
@app.route("/chart/<symbol>/<freq>/<opt>/<kind>")
def chart(symbol,freq=None,opt=None,kind=None):
    sym = sm.get(symbol)
    df = sym.df
    
    f = cio.StringIO()

    
    if freq:
        df = df.asfreq(freq, method='ffill')
    
    if opt == 'pct':
        df = df.pct_change(1)
    
    if kind:
        ax = df.plot(kind=kind, title=sym.description, legend=False)
    else:
        ax = df.plot(title=sym.description, legend=False)
        

    ax.set_xlabel(sym.name)
    ax.set_ylabel(sym.units)
        
    
    fig = ax.get_figure()
    
    fig.savefig(f, format='png')
    
    header = {'Content-type' : 'image/png'}
    f.seek(0)
    data = f.read()
    
    return data, 200, header

@app.route("/export/<ext>/<symbol>")
@app.route("/export/<ext>/<symbol>/<freq>")
def export(ext, symbol, freq=None):
    
    sym = sm.get(symbol)
    
    f = cio.StringIO()
    
    df = sym.df
    
    if freq:
        df = df.asfreq(freq, method='ffill')
    
    if ext == 'csv':
        sym.df.to_csv(f, sep=',', header=True)
        header = {'Content-Disposition' : "attachment; filename=" + sym.name + ".csv"}
        f.seek(0)
        data = f.read()
        return data, 200, header    
        
    elif ext == 'xlsx':
        fn = sym.name + ".xls"
        wrtr = pd.ExcelWriter(fn, engine='xlsxwriter')
        wrtr.book.filename = f
        df.to_excel(wrtr, sheet_name=sym.name)
        wrtr.save()
        header = {'Content-Disposition' : "attachment; filename=" + sym.name + ".xls"}
        f.seek(0)
        data = f.read()
        return data, 200, header

#    response = make_response(f)
#    
#    response.headers['Content-Disposition'] = "attachment; filename=" + sym.name + ".xlsx"
#
#    return response

@app.route("/orfs/<symbol>")
def orfs(symbol):
    sym = sm.get(symbol)
    data = sym._all_datatable_data()
    return render_template('symbol_orfs.html', symbol=sym, data=data)

@app.route("/c/<symbol>")
def cacheit(symbol):
    sym = sm.get(symbol)
    result = sym.cache()
    tit = "Recaching Results"
    mac = sym.name + " was (likely) re-cached successfully!"
    nfo = Markup(result.html)
    return render_template('confirmation.html', msg_title=tit, msg_macro=mac, msg_info=nfo)

@app.route("/t/<tag>")
def tagged(tag):
    print tag
    name = False
    desc = False
    tags = True
    meta = False
    syms = sm.search(StringOnly=True)
    
    results = sm.search(tag, name=name, desc=desc, tags=tags, meta=meta, dolikelogic=False)
    if len(results) == 0:
        msg = "No Symbols Tagged {} Found".format(tag)
    else:
        msg = ""

    return render_template('home.html', msg=msg, symbols=syms, qry="", results=results, name=name, desc=desc, tags=tags, meta=meta)

@app.route("/q/", methods=['POST'])
def queried_browser():
    qry = request.form['qry']
    name = request.form.has_key('scname')
    desc = request.form.has_key('scdesc')
    tags = request.form.has_key('sctags')
    meta = request.form.has_key('scmeta')
    syms = sm.search(StringOnly=True)
    
    print syms
    if (len(qry) > 0) and (name or desc or tags or meta):
        results = sm.search(qry, name=name, desc=desc, tags=tags, meta=meta)
        msg = "No Results Found"
    else:
        results = []
        msg = "Must type something, and select either name, description, tags or meta."
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=results, name=name, desc=desc, tags=tags, meta=meta)

@app.route("/")
def default_browser():
    qry = "Type here to search Trump"
    syms = sm.search(StringOnly=True)
    msg = "Type to Search"
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=[])        

@app.route("/s/<symbol>")
def symbol_page(symbol):
    sym = sm.get(symbol)
    metaattr = [meta.attr for meta in sym.meta]
    metaattr.sort()
    S = sym.df[sym.name]
    S.name = None
    ind = str(type(S.index)).split("'")[1]
    lind = len(S)
    
    tmp = str(S.tail(4))
    tmp = tmp.split("dtype")[0]
    tailhtml = Markup(tmp)
    
    dtype =  str(S.dtype)
    return render_template('symbol_page.html', symbol=sym, sdf=S, dtype=dtype, ind=ind,lind=lind, sdfhtml=tailhtml, metaattr=metaattr)

if __name__ == "__main__":
    app.run(debug=True)