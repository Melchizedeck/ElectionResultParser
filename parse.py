from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import requests
from lxml import html
import argparse
import logging
import re
import json
import os

log = logging.getLogger("main")
headers ={'user-agent':'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'}
baseAddress = "https://www.resultats-elections.interieur.gouv.fr/presidentielle-2022/"
xpathNamespace={"re": "http://exslt.org/regular-expressions"}

"""
télécharge une page de site et renvoie un tuple associant la zone à une URL 
"""
def browse(session, url, path ):
    request = session.get(url, stream=True, allow_redirects=True, headers=headers)
    encoding = 'utf-8'
            
    if request.encoding:
        encoding = request.encoding
    
    decoded = request.content.decode(encoding)

    tree = html.fromstring(decoded)
    
    lines = tree.xpath(path, namespaces=xpathNamespace)
    for line in lines:
        yield  ( line.text, urljoin(request.url, line.attrib['href']))

"""
analyse la page de résultat electoraux d'une zone
"""
def ParseResultats(url):
    with requests.Session() as session:
        request = session.get(url, stream=True, allow_redirects=True, headers=headers)
        encoding = 'utf-8'
                
        if request.encoding:
            encoding = request.encoding
        
        decoded = request.content.decode(encoding)
        if args.temp:
            with open(args.temp,'w', encoding=encoding) as f:
                f.write(decoded)

        tree = html.fromstring(decoded)
        candidats = tree.xpath("//table[contains(@class,'tableau-resultats-listes-ER')]/tbody/tr")

        result = {'candidats':[]}
        for candidat in candidats:
            columns = candidat.xpath("td")
            result['candidats'].append( {
                'name':columns[0].text,
                'voiceCount':int(columns[1].text.replace(' ','')),
                'inscritsPourcent':float(columns[2].text.replace(',','.')),
                'exprimesPourcent':float(columns[3].text.replace(',','.'))
            
            })
            
        mentions = tree.xpath("//table[contains(@class,'tableau-mentions')]/tbody/tr")
        
        for line in mentions:
            columns = list(c.text for c in line.xpath("td"))
            if columns[0]=="Inscrits":
                result['inscrits']={'count':int(columns[1].replace(' ',''))}
            if columns[0]=="Abstentions":
                result['abstentions']={'count':int(columns[1].replace(' ','')),'inscritsPourcent':float(columns[2].replace(',','.'))}
            if columns[0]=="Votants":
                result['votants']={'count':int(columns[1].replace(' ','')),'inscritsPourcent':float(columns[2].replace(',','.'))}
            if columns[0]=="Blancs":
                result['blancs']={'count':int(columns[1].replace(' ','')),'inscritsPourcent':float(columns[2].replace(',','.')),'exprimesPourcent':float(columns[3].replace(',','.'))}
            if columns[0]=="Nuls":
                result['nuls']={'count':int(columns[1].replace(' ','')),'inscritsPourcent':float(columns[2].replace(',','.')),'exprimesPourcent':float(columns[3].replace(',','.'))}
            if columns[0]=="Exprimés":
                result['exprimés']={'count':int(columns[1].replace(' ','')),'inscritsPourcent':float(columns[2].replace(',','.')),'exprimesPourcent':float(columns[3].replace(',','.'))}

        return result


"""
parcourt l'ensemble des pages disponibles en récupérant les scrutins par zone
"""
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--json", metavar='json', type=str, help="json out file", required=True)
    parser.add_argument("--jsonIndent", metavar='jsonIndent', type=int, help="json indentation space count", required=False)
    parser.add_argument("--logLevel", metavar='logLevel', type=str, help="log level", required=False)
    parser.set_defaults(jsonIndent = None)
    parser.set_defaults(logLevel = None)
    args = parser.parse_args()
    
    if args.logLevel:
        logging.basicConfig(level=os.environ.get("LOGLEVEL", args.logLevel))
    indexURL = "https://www.resultats-elections.interieur.gouv.fr/presidentielle-2022/index.html"
    #parcours du site (france, régions, départements, [indexes], villes)
    with requests.Session() as session:
        nodes = []
        for name, url in browse(session, indexURL, "//a[re:match(@href,'FE\.html$')]"):
            log.info("parsing '{}'".format(name))
            nodes.append({'level':0, 'name':name, 'url':url, 'children':[], 'result':ParseResultats(url)})
        franceNode = nodes[0]     

        for regionName, regionURL in browse(session, indexURL, "//a[re:match(@href,'\./[0-9]+/[0-9]+\.html$')]"):
            log.info("parsing '{}'".format(regionName))
            regionNode = {'level':1, 'name':regionName, 'url':regionURL, 'children':[], 'result':ParseResultats(regionURL)}
            franceNode['children'].append(regionNode)
            for departmentName, departmentURL in browse(session, regionURL, "//a[re:match(@href,'\.\./[0-9]+/[0-9A-Z]+/[0-9A-Z]+\.html$')]"):
                log.info("parsing '\t{}'".format(departmentName))
                departmentNode = {'level':2, 'name':departmentName, 'url':departmentURL, 'children':[], 'result':ParseResultats(departmentURL)}
                regionNode['children'].append(departmentNode)
                for departmentIndexName, departmentIndexURL in browse(session, departmentURL, "//a[re:match(@href,'\.\./\.\./[0-9]+/[0-9A-Z]+/[0-9A-Z]+\.html$')]"):
                    for townName, townURL in browse(session, departmentIndexURL, "//a[re:match(@href,'\.\./\.\./[0-9]+/[0-9A-Z]+/[0-9]+[A-Z]?[0-9]+\.html$')]"):
                        log.info("parsing '\t\t{}'".format(townName))
                        townNode={'level':3, 'name':townName, 'url':townURL, 'result':ParseResultats(townURL) }
                        departmentNode['children'].append(townNode)

        
        if args.json :
            log.info("saving '{}'".format(args.json))
            with open(args.json,'w') as f: 
                json.dump(franceNode,f, indent=args.jsonIndent)

