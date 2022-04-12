import argparse
import json
import os
import matplotlib.pyplot
import seaborn
import pandas


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", metavar='input', type=str, help="json input file", required=True)
    parser.add_argument("--output", metavar='output', type=str, help="output file")

    args = parser.parse_args()
    field = 'exprimesPourcent' # 'exprimesPourcent' 'inscritsPourcent'
    node = None
    with open(args.input,'r') as f: 
        node = json.load(f)
        
    regions = node['children']
    departments = [department for region in regions for department in region['children']]
    towns = [town for department in departments for town in department['children']]

    areaLevels={
        "régions" : regions,
        "départements" : departments,
        "villes" : towns,
    }
    candidatName=[]
    groupNames=[]
    values=[]
    for groupName, areas in areaLevels.items():
        candidatResults = [candidat for area in areas for candidat in area['result']['candidats']]
        for cr in candidatResults:
            candidatName.append(' '.join(cr['name'].split(' ')[2:]))
            values.append(cr[field])
            groupNames.append(groupName)

    df=pandas.DataFrame({ 'candidat' : candidatName, 'scrutin': values, 'group':groupNames })

    matplotlib.rcParams['figure.figsize']=[15,8]
    matplotlib.rcParams['figure.dpi']=200
    
    matplotlib.rcParams['figure.subplot.left']=0.045
    matplotlib.rcParams['figure.subplot.right']=0.99
    matplotlib.rcParams['figure.subplot.top']=0.98
    matplotlib.rcParams['figure.subplot.bottom']=0.07
    ax = seaborn.boxplot(x='candidat', y='scrutin', hue='group', width=0.5, data=df, showfliers = False)
    ax.set_ylim(-1, 60)
    
    #matplotlib.pyplot.title(title, loc="left")
    if args.output:
        matplotlib.pyplot.savefig(args.output)
    else:
        matplotlib.pyplot.show()
    matplotlib.pyplot.clf()

