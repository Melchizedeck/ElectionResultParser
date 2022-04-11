import argparse
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def groupResults(areas, fieldName):
    data = {}
    candidatResults = [candidat for area in areas for candidat in area['result']['candidats']]
    for candidat in candidatResults:
        if not candidat['name'] in data:
            data[candidat['name']]=[candidat[fieldName]]
        else:
            data[candidat['name']].append(candidat[fieldName])
    return data


def display(title, data):
    frames=[]
    for candidat in data.items():
        name = candidat[0].split(' ')[2]
        frames.append(pd.DataFrame({ 'candidat' : name, 'scrutin': candidat[1] }))
    df=frames[0]
    for f in frames[1:]:
        df = df.append(f)
    # Usual boxplot
    sns.boxplot(x='candidat', y='scrutin', data=df)
    
    plt.title(title, loc="left")
    plt.show()
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", metavar='input', type=str, help="json input file", required=True)
    parser.set_defaults(jsonIndent = None)
    parser.set_defaults(logLevel = None)
    args = parser.parse_args()
 
    field = 'inscritsPourcent' # 'exprimesPourcent' 'inscritsPourcent'
 
    with open(args.input,'r') as f: 
        node = json.load(f)
        regions = node['children']
        departments = [department for region in regions for department in region['children']]
        towns = [town for department in departments for town in department['children']]
        
        areaLevels={
            "Regions" : regions,
            "Departments" : departments,
            "Towns" : towns,
        }
        
        
        for name, areas in areaLevels.items():
            data = groupResults(areas, field)
            display(name, data)

