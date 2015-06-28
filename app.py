f = open("trumpui.log",'wb+')
f.write("pre flask import")
from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack, make_response, \
    send_file

f.write("pre string io import")

import datetime as dt
import cStringIO as cio
import sys, os
import pandas as pd

import trump
from trump import SymbolManager

import matplotlib as m
import matplotlib.pyplot as plt
from jinja2 import Markup
sm = SymbolManager()

import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='trumpweb')



from collections import namedtuple, Counter

SymStatus = namedtuple("SymStatus", ['name', 'completed', 'attempted', 'state', 'desc'])

curdir = os.path.dirname(os.path.realpath(__file__))
plotstyles = os.path.join(curdir,"plotstyles")

try:
    plt.style.use(os.path.join(plotstyles,"default.mplstyle"))
except:
    print "Couldn't load style sheet, likely have matplotlib < 1.4"
    
app = Flask(__name__)

f.write("done making flask object")

def symbfbutton(symbol, handlepoint):
    bf = symbol.handle.setting(handlepoint)
    
    flagstate = zip(bf.flags, bf.bools)
    
    link = "/ch/{}/{}/".format(symbol.name, handlepoint)
    link = link + "{}"
    
    def switchr(b):
        if b:
            return " class='btn btn-default btn-xs active' style='font-size : 7px; padding: 0px 2px;' role='button' "
        else:
            return " class='btn btn-default btn-xs' style='font-size : 7px; padding: 0px 2px;' role='button' "
        
    ret = ["<a href='{}' {}>{}</a>".format(link.format(i), switchr(flgst), flg) for i, (flg, flgst) in enumerate(flagstate)]
    ret = " ".join(ret)
    return Markup(ret)
app.jinja_env.globals.update(symbfbutton=symbfbutton)

def feedbfbutton(symbol, feed, handlepoint):
    bf = feed.handle.setting(handlepoint)
    
    flagstate = zip(bf.flags, bf.bools)
    
    link = "/ch/{}/{}/".format(symbol.name, handlepoint)
    link = link + "{}/" + str(feed.fnum)
    
    def switchr(b):
        if b:
            return " class='btn btn-default btn-xs active' style='font-size : 7px; padding: 0px 2px;' role='button' "
        else:
            return " class='btn btn-default btn-xs' style='font-size : 7px; padding: 0px 2px;' role='button' "
        
    ret = ["<a href='{}' {}>{}</a>".format(link.format(i), switchr(flgst), flg) for i, (flg, flgst) in enumerate(flagstate)]
    ret = " ".join(ret)
    return Markup(ret)
app.jinja_env.globals.update(feedbfbutton=feedbfbutton)


def symurl(sym):
    return Markup(r"<a href=/s/{0}>{0}</a>".format(sym))
app.jinja_env.globals.update(symurl=symurl)


def taglink(tag):
    return Markup(r'<a class="btn btn-xs btn-success" href="/t/{0}">{0}</a>'.format(tag))
app.jinja_env.globals.update(taglink=taglink)

def cleanmaxmin(symbol):
    mxmn = symbol._max_min()
    
    def tostr(obj):
        if isinstance(obj, dt.datetime):
            return obj.strftime("%Y-%m-%d")
        else:
            return str(obj)
     
    return Markup(" to ".join([tostr(mm) for mm in mxmn]))
app.jinja_env.globals.update(cleanmaxmin=cleanmaxmin)   


@app.route("/about")
def about():
    eng = sm.eng
    mac = "Currently Connected to..."
    info = Markup("<br>".join([str(obj) for obj in [eng.name,eng, eng.dialect]]))
    
    info = info + Markup("<br>".join([obj.__file__ for obj in [pd, trump, m]]))
    
    try:
        import xlsxwriter
        info = info + Markup("<br>")
        info = info + Markup(xlsxwriter.__file__)
    except:
        info = info + Markup("Failed to find xlsxwriter")
    
    info = info + Markup("<br><br>")
    
    info = info + Markup("<br>" + plotstyles)
    
    info = info + Markup("<br><br>")
    
    info = info + Markup("<br>".join([obj.__version__ for obj in [pd, trump, m]]))
    
    info = info + Markup("<br><br>")
    
    info = info + Markup("<br>".join([obj for obj in sys.path]))
    
    return render_template('about.html', msg_title="About Trump", msg_macro=mac, msg_info=info)

@app.route("/raiseanerror")
def raiseanerror():
    somedict = {'jeff' : 'wins', 'trump': 'rock'}
    
    print somedict
    
    raise Exception("Nothing , jeff put this here")


def formattedpy(obj):
    return Markup("<pre>" + str(obj) + "</pre>")

@app.route("/a/<symbol>")
@app.route("/a/<symbol>/<freq>")
def a(symbol, freq=None):
    sym = sm.get(symbol)
    df = sym.df
    
    title = sym.name + " Analyze"
    
    if freq:
        title = "{} @ freq {}".format(title, freq)
        df = df.asfreq(freq, method='ffill')

    ret = Markup("<h3>Index Information</h3>")
    ret = ret + formattedpy(df.index)
    
    ret = ret + formattedpy(df.dtypes)
    
    dfs = [df, df.pct_change(1)]
    
    titles = ["<h3>Raw</h3>","<h3>Percent Change</h3>"]
    for i, df in enumerate(dfs):
        ret = ret + Markup(titles[i])
        ret = ret + formattedpy(df.head(5))

        ret = ret + formattedpy(df.tail(5))

        ret = ret + formattedpy(df.describe())
    
    return render_template('confirmation.html', msg_title=title, msg_macro=sym.description, msg_info=ret, symbol=sym)

@app.route("/index/<symbol>")
def index(symbol, freq=None):
    sym = sm.get(symbol)
    df = sym.df
    
    title = sym.name + " Index"

    ret = Markup("<h3>Index Information</h3>")
    ret = ret + formattedpy(df.index)
    
    ret = ret + formattedpy((df.index[0],df.index[-1], ))

    ret = ret + formattedpy(sym.index)
    
    ret = ret + formattedpy(sym.index.getkwargs())
    
    return render_template('confirmation.html', msg_title=title, msg_macro=sym.description, msg_info=ret, symbol=sym)

@app.route("/data/<symbol>")
def data(symbol, freq=None):
    sym = sm.get(symbol)
    df = sym.df
    
    title = sym.name + " Data"

    ret = Markup("<h3>Data Information</h3>")
    ret = ret + formattedpy(sym.dtype)
    ret = ret + formattedpy(df.dtypes)
    
    ret = ret + Markup("<h3>Dataframe</h3>")
    with pd.option_context('display.max_rows', len(df)):
        ret = ret + formattedpy(str(df))

    return render_template('confirmation.html', msg_title=title, msg_macro=sym.description, msg_info=ret, symbol=sym)


@app.route("/munging/<symbol>")
def munging(symbol):
    sym = sm.get(symbol)
    df = sym.df
    
    title = sym.name + " Munging"
    
    ret = Markup("")
    
    for fd in sym.feeds:
        ret = ret + Markup("<h3>Feed " + str(fd.fnum) + "</h3>")
        mgn = list(fd.munging)
        if len(mgn) > 0:
            for mg in fd.munging:
                ret = ret + formattedpy(mg)
        else:
            ret = ret + "No Munging for this Feed"
    
    return render_template('confirmation.html', msg_title=title, msg_macro=sym.description, msg_info=ret, symbol=sym)

@app.route("/validity/<symbol>")
def validity(symbol):
    sym = sm.get(symbol)
    
    title = sym.name + " Validity"
    
    ret = Markup("")
    
    vald = list(sym.validity)
    
    if sym.isvalid:
        ans = "IS VALID"
    else:
        ans = "IS NOT VALID"
        
    ret = ret + Markup("This symbol <b>{}</b>".format(ans))
    
    if len(vald) > 0:
        for vl in vald:
            ret = formattedpy(vl)
    else:
        et = ret + "No Validity for this Symbol"

    return render_template('confirmation.html', msg_title=title, msg_macro=sym.description, msg_info=ret, symbol=sym)


@app.route("/fig/<symbol>")
@app.route("/fig/<symbol>/<freq>/<opt>/<kind>")
def fig(symbol,freq=None,opt=None,kind=None):
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
    fig.set_size_inches(8,4.5)
    fig.savefig(f, format='png', dpi=150)
    
    
    f.seek(0)
    
    return send_file(f, mimetype='image/png')
    # To display the image...
    # header = {'Content-type' : 'image/png'}
    # data = f.read()
    # return data, 200, header

@app.route("/chart/<symbol>")
@app.route("/chart/<symbol>/<freq>/<opt>/<kind>")
def chart(symbol,freq=None,opt=None,kind=None):
    symbol = sm.get(symbol)
    return render_template('chart.html', symbol=symbol, freq=freq, opt=opt, kind=kind)

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
        fn = sym.name + ".xlsx"
        wrtr = pd.ExcelWriter(fn, engine='xlsxwriter')
        wrtr.book.filename = f
        df.to_excel(wrtr, sheet_name=sym.name)
        wrtr.save()
        header = {'Content-Disposition' : "attachment; filename=" + sym.name + ".xlsx"}
        f.seek(0)
        data = f.read()
        return data, 200, header

@app.route("/orfs/<symbol>")
def orfs(symbol):
    sym = sm.get(symbol)
    data = sym._all_datatable_data()
    data = [(i,row) for i,row in enumerate(data)]
    orfss = sym.existing_orfs()
    
    ors = orfss['or']
    ors.sort(key=lambda o: (o.ind, o.ornum))
    
    fss = orfss['fs']
    fss.sort(key=lambda f: (f.ind, f.fsnum))
    
    return render_template('symbol_orfs.html', symbol=sym, data=data, ors=ors, fss=fss)

@app.route("/tc/<tag>")
def tc(tag):
    """ Cache a symbol """
    syms = sm.search(tag, tags=True)
    
    for sym in syms:
        channel.basic_publish(exchange='',
                              routing_key='trumpweb',
                              body=sym.name)
        print " [x] Told cacher to cache {}".format(sym.name)

    tit = "Cache in progress..."
    mac = "Caching of tag {} (likely) worked".format(tag)
    nfo = "Check your inbox, server logs, trump logs for more info"

    return render_template('confirmation.html', msg_title=tit, msg_macro=mac, msg_info=nfo, symbol=sym)


@app.route("/c/<symbol>")
def c(symbol):
    """ Cache a symbol """
    sym = sm.get(symbol)
    channel.basic_publish(exchange='',
                          routing_key='trumpweb',
                          body=symbol)
    print " [x] Told cacher to cache {}".format(symbol)

    tit = "Cache in progress..."
    mac = "Caching of {} (likely) worked".format(symbol)
    nfo = "Check your inbox, server logs, trump logs for more info"

    return render_template('confirmation.html', msg_title=tit, msg_macro=mac, msg_info=nfo, symbol=sym)

@app.route("/deleteorfs/<which>/<sym>/<orfs_num>")
def deleteorfs(which, sym, orfs_num):
    sm.delete_orfs(sym, which, orfs_num)
    sym = sm.get(sym)
    sym.cache()
    nfo = "Deleted {} # {} for {}".format(which, orfs_num, sym.name)
    return render_template('confirmation.html', msg_title=sym.name, msg_macro=sym.description, msg_info=nfo)

@app.route("/ch/<sym>/<handlepoint>/<togglebit>")
@app.route("/ch/<sym>/<handlepoint>/<togglebit>/<feednum>")
def changehandle(sym,handlepoint,togglebit,feednum=-1):
    sym = sm.get(sym)
    togglebit = int(togglebit)
    feednum = int(feednum)
    
    if feednum == -1:
        bf = sym.handle.setting(handlepoint)
    else:
        bf = sym.feeds[feednum].handle.setting(handlepoint)
    
    bf[togglebit] = not bf[togglebit]
    
    if feednum == -1:
        setattr(sym.handle, handlepoint, bf)
    else:
        setattr(sym.feeds[feednum].handle, handlepoint, bf)
        
    return redirect(url_for('s',symbol=sym.name))

@app.route("/t/<tag>")
def t(tag):
    """ Tag Searching..."""
    syms = sm.search(stronly=True)
    
    results = sm.search(tag, tags=True, dolikelogic=False)
    if len(results) == 0:
        msg = "No Symbols Tagged {} Found".format(tag)
    else:
        msg = ""
    return render_template('home.html', msg=msg, symbols=syms, qry="", results=results, name=False, desc=False, tags=True, meta=False)

@app.route("/status")
@app.route("/status/<tag>")
def status(tag=None):
    
    if tag:
        syms = sm.search(tag,tags=True)
    else:
        syms = sm.search()
    
    completed = [sym.last_cache() for sym in syms]
    attempts = [sym.last_cache('START') for sym in syms]
    goodbad = [a > c for a,c in zip(completed, attempts)]
    desc = [sym.description for sym in syms]
    
    statuses = [SymStatus(sym.name, c, a, s, d) for sym, c, a, s, d in zip(syms, completed, attempts, goodbad, desc)]
    
    return render_template('status_list.html', statuses=statuses)

@app.route("/tags")
@app.route("/tags/<tag>")
def tags(tag=None):
    
    if tag:
        syms = sm.search(tag,tags=True)
    else:
        syms = sm.search()
    
    tags = [[t.tag for t in sym.tags] for sym in syms]
    
    tags = [item for sublist in tags for item in sublist]
    
    counted = Counter(tags)
    unique = counted.keys()
    unique.sort()
    
    return render_template('tags_list.html', count=counted, tags=unique)


@app.route("/q/", methods=['POST'])
def queried_browser():
    """ Query browser """
    qry = request.form['qry']
    name = request.form.has_key('scname')
    desc = request.form.has_key('scdesc')
    tags = request.form.has_key('sctags')
    meta = request.form.has_key('scmeta')
    syms = sm.search(stronly=True)
    
    print syms
    if (len(qry) > 0) and (name or desc or tags or meta):
        results = sm.search(qry, name=name, desc=desc, tags=tags, meta=meta)
        msg = "No Results Found"
    else:
        results = []
        msg = "Must type something, and select either name, description, tags or meta."
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=results, name=name, desc=desc, tags=tags, meta=meta)

@app.route("/")
def home():
    qry = "Type here to search Trump"
    syms = sm.search(stronly=True)
    msg = "Type to Search"
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=[])        

@app.route("/orfssaved/", methods=['POST'])
def orfssaved():
    usrinput = request.form
    
    comment = usrinput['comment']
    sym = usrinput['symbol']
    sym = sm.get(sym)
    
    # Some major thinking needs to be done here...to implement this in a robust way, for all data and index 
    # types
    
    def isgood(v):
        if len(v) > 0 and v != "None":
            return True
        else:
            return False
    
    def togood(v):
        return float(v)
    
    orfss = {(int(key[2:]),key[:2]) : togood(value) for key,value in usrinput.iteritems() if isgood(value) and key[:2] in ('or','fs') and key[:4] != 'orig'}
    
    origorfss = {(int(key[6:]),key[:2]) : togood(value) for key,value in usrinput.iteritems() if isgood(value) and key[4:6] in ('or','fs')}
    
    for orfs, value in orfss.iteritems():
        if orfs in origorfss:
            doadd = orfss[orfs] != origorfss[orfs]
        else:
            doadd = True
        
        if doadd:
            sm.add_existing_ind_orfs(orfs[1], sym, orfs[0], value, comment) 
    
    sym.cache()
    
    nfo = "{} {}".format(str(orfss), comment)
    return render_template('confirmation.html', msg_title=sym.name, msg_macro=sym.description, msg_info=nfo, symbol=sym)

@app.route("/installtrump")
def installtrump():
    from trump import SetupTrump
    SetupTrump()
    return "Trump likely installed correctly"

@app.route("/installsymbols")
def installsymbols():
    import setupsymbols
    return "Likedly done creating a bunch of symbols"

@app.route("/s/<symbol>")
def s(symbol):
    """ Symbol Page """
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

@app.route("/delete/<symbol>")
def delete(symbol):
    """ Symbol Page """
    sym = sm.get(symbol)
    name = sym.name
    sm.delete(sym)
    
    tit = "Deleted " + name
    mac = "Deletion of the symbol was successful..."
    nfo = "...Using SymbolManager.delete()"
    # TODO check to make sure it's actually deleted
    # Plus, some likely GitHub Issue
    return render_template('confirmation.html', msg_title=tit, msg_macro=mac, msg_info=nfo)

f.write("\n My name is {}".format(__name__))


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    fh = RotatingFileHandler("trumpuisite.log", 'a')
    fh.setLevel(logging.WARNING)
    app.logger.addHandler(fh)

f.write("\I must have figured out how to handle")

if __name__ == "__main__":
    f.write("\n we shouldn't get here")
    if len(sys.argv) > 1:
        app.run(debug=True)
    else:
        app.run('0.0.0.0')

f.write("\n all done!")
f.close()
connection.close()