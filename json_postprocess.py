import argparse
import json
import os


headers ={'user-agent':'Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0'}
baseAddress = "https://www.resultats-elections.interieur.gouv.fr/presidentielle-2022/"
xpathNamespace={"re": "http://exslt.org/regular-expressions"}


"""
parcourt l'ensemble des pages disponibles en récupérant les scrutins par zone
"""
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", metavar='input', type=str, help="json input file", required=True)
    parser.add_argument("--output", metavar='output', type=str, help="json input file", required=True)
    parser.add_argument("--jsonIndent", metavar='jsonIndent', type=int, help="json indentation space count", required=False)
    parser.set_defaults(jsonIndent = None)
    parser.set_defaults(logLevel = None)
    args = parser.parse_args()
    
    if args.logLevel:
        logging.basicConfig(level=os.environ.get("LOGLEVEL", args.logLevel))
        
    data = None
    with open(args.input,'r') as f: 
        data = json.load(f)
        
    with open(args.output,'w') as f:
        json.dump(data,f, indent=args.jsonIndent)


