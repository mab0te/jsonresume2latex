#!/usr/bin/env python

from argparse import ArgumentParser
from json import load
from jinja2 import Environment, FileSystemLoader
from re import search

COLORS=["black","blue","burgundy","green","grey","orange","purple"]
THEMES=["banking","casual","classic","empty","fancy","oldstyle"]

parser = ArgumentParser()
parser.add_argument("resume", help="Path to the JSON Resume.")
parser.add_argument("-o", "--output", required=True, help="Output file path.")
parser.add_argument("-p","--picture", help="Path to the resume picture.")
parser.add_argument("-m","--margin", help="Margin ratio, e.g: 0.75.")
parser.add_argument("-c","--color", choices=COLORS, help="Resume color theme.")
parser.add_argument("-t","--theme", choices=THEMES, help="Resume theme.")

def latex_escape(s:str):
    special_chars = ["_","#","%"]
    ret = s
    for c in special_chars:
        ret = ret.replace(c, f"\\{c}")
    return ret

def sanitize_deep(o: object):
    if isinstance(o, dict):
        d = {}
        for k in o:
            d[k] = sanitize_deep(o[k])
        return d
    elif isinstance(o, list):
        return [sanitize_deep(li) for li in o]
    elif isinstance(o, str):
        return latex_escape(o)
    else:
        print(f"{o}: returned as is")
        return o

args = parser.parse_args()

with open(args.resume, "r") as cv_file:
    cv_data = load(cv_file)

cv_data["picture"] = args.picture
cv_data["margin"] = args.margin
cv_data["color"] = args.color
cv_data["theme"] = args.theme

cv_data = sanitize_deep(cv_data)
print(cv_data)

for publication in cv_data["publications"]:
    if "website" in publication:
        publication["url"] = publication["website"]
    if "url" in publication:
        matched = search(r"(?<=https://)([^/]+)", publication["url"])
        domain = matched[1]
        publication["publisher"] = f"\\href{{{publication['url']}}}{{{domain}}}"

env = Environment(
    loader=FileSystemLoader("templates"),
    variable_start_string="${{")
cv_template = env.get_template("template.tex")

rendered = cv_template.render(cv_data)

with open(args.output, "w") as cv_output:
    cv_output.write(rendered)