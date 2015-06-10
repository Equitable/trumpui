# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 16:02:28 2015

@author: jnm
"""

from trump.orm import SymbolManager
from trump.templating.templates import FFillIT, WorldBankFT, StLouisFEDFT, QuandlFT, GoogleFinanceFT, YahooFinanceFT

sm = SymbolManager()

xiu = sm.create('XIU', overwrite=True)
xiu.add_tags(['ETF', 'iShares'])
xiu.add_meta(Geography='Canada', AssetClass='Equity', MER="0.07")
xiu.set_description("S&P/TSX 60 Index Fund")
xiu.set_units("CAD/unit")
#xiu.add_feed(GoogleFinanceFT('TSE:XIU'))
xiu.add_feed(YahooFinanceFT('XIU.TO'))
xiu.cache()

spy = sm.create('SPY', overwrite=True)
spy.add_tags(['ETF', 'equity'])
spy.set_description("SPDR S&P 500 ETF Trust")
spy.add_meta(Geography='USA', AssetClass='Equity', Index='S&P 500', MER="0.11", CUSIP="78462F103", Exchange="NYSE")
spy.set_units("USD/unit")
spy.add_feed(YahooFinanceFT('SPY'))
spy.cache()

tsla = sm.create('TSLA', overwrite=True)
tsla.add_tags(['ETF', 'equity', 'Company'])
tsla.set_description("Tesla Motor Company Common Stock")
tsla.add_meta(Geography='USA', AssetClass='Equity', Sector='Automotive')
tsla.set_units("USD/unit")
tsla.add_feed(YahooFinanceFT('TSLA'))
tsla.add_feed(GoogleFinanceFT('TSLA'))
#tsla.add_feed(QuandlFT('GOOG/NASDAQ_TSLA', fieldname='Close'))
tsla.cache()

cpi = sm.create('CPI', overwrite=True)
cpi.add_tags(['Consumer', 'Price Index', 'Seasonally Adjusted'])
cpi.set_description("Consumer Price Index for All Urban Consumers: All Items")
cpi.add_meta(Geography='USA', Factor='Inflation', Publisher="BLS")
cpi.set_units("MoM")
cpi.add_feed(StLouisFEDFT('CPIAUCSL'))
cpi.cache()

from pandas.io import wb

results = wb.search('GDP*')
results = results[results.id == 'NY.GDP.MKTP.CD']
r = results.T.to_dict().values()[0]
r = {key.replace("source","WB") : value for key, value in r.iteritems()}

ctrycodes = ['ABW', 'AFG', 'AGO', 'ALB', 'AND', 'ARE', 'ARG', 'ARM', 'ASM', 'ATG', 'AUS', 'AUT', 'AZE', 'BDI', 'BEL', 'BEN', 'BFA', 'BGD', 'BGR', 'BHR', 'BHS', 'BIH', 'BLR', 'BLZ', 'BMU', 'BOL', 'BRA', 'BRB', 'BRN', 'BTN', 'BWA', 'CAF', 'CAN', 'CHE', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CYM', 'CYP', 'CZE', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESP', 'EST', 'ETH', 'FIN', 'FJI', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GEO', 'GHA', 'GIN', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GRL', 'GTM', 'GUM', 'GUY', 'HKG', 'HND', 'HRV', 'HTI', 'HUN', 'IDN', 'IMN', 'IND', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JOR', 'JPN', 'KAZ', 'KEN', 'KGZ', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LAO', 'LBN', 'LBR', 'LBY', 'LCA', 'LIE', 'LKA', 'LSO', 'LTU', 'LUX', 'LVA', 'MAC', 'MAF', 'MAR', 'MCO', 'MDA', 'MDG', 'MDV', 'MEX', 'MHL', 'MKD', 'MLI', 'MLT', 'MMR', 'MNE', 'MNG', 'MNP', 'MOZ', 'MRT', 'MUS', 'MWI', 'MYS', 'NAM', 'NCL', 'NER', 'NGA', 'NIC', 'NLD', 'NOR', 'NPL', 'NZL', 'OMN', 'PAK', 'PAN', 'PER', 'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRK', 'PRT', 'PRY', 'PSE', 'PYF', 'QAT', 'ROU', 'RUS', 'RWA', 'SAU', 'SDN', 'SEN', 'SGP', 'SLB', 'SLE', 'SLV', 'SMR', 'SOM', 'SRB', 'SSD', 'STP', 'SUR', 'SVK', 'SVN', 'SWE', 'SWZ', 'SXM', 'SYC', 'SYR', 'TCA', 'TCD', 'TGO', 'THA', 'TJK', 'TKM', 'TLS', 'TON', 'TTO', 'TUN', 'TUR', 'TUV', 'TZA', 'UGA', 'UKR', 'URY', 'USA', 'UZB', 'VCT', 'VEN', 'VIR', 'VNM', 'VUT', 'WSM', 'YEM', 'ZAF', 'ZMB', 'ZWE']
badlist = []
for cc in ctrycodes:

    # just to make a copy
    meta = dict(r)
    tickr = "GDP_" + cc
    wbi = sm.create(tickr, overwrite=True)
    
    #awkward, that this is the only way to get this from the API
    country = wb.download(indicator='NY.GDP.MKTP.CD',country=cc).index.levels[0][0]
    
    wbi.add_tags(["economics", "world bank", "GDP"])
    wbi.set_description(meta['name'])
    del meta['name']
    meta['ISO 3166-1 Country Code'] = cc
    meta['Country'] = country
    wbi.add_meta(**meta)
    wbi.set_units("NoUnits")
    wbi.add_feed(WorldBankFT('NY.GDP.MKTP.CD',cc, start='1950', end='2015'))
    
    AnnualIndex = FFillIT('A')
    wbi.set_indexing(AnnualIndex)
    
    wbi.cache()


print badlist

sm.finish()