# Election Result Parser

an html parser that fill a JSON structure with french election results in order to compare votes distribution for each candidate

## Purpose

download elections data and check ratios in order to fight (my own) comspirationism 

## Uglyness
that code is made as fast as I can, in order to learn html parsing.

## Usage

```bash
python parse.py --json results.json
```

```bash
python compute_distribution.py --input results.json
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
