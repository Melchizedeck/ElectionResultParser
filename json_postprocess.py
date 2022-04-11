import argparse
import json
import os

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


