from __future__ import annotations
import argparse, yaml
from renderer import POSTS, existing_numbers

def next_number():
    nums=existing_numbers(); return nums[-1]+1 if nums else 1

def write(number,data):
    target=POSTS/f"{number:03d}.yaml"
    if target.exists(): raise FileExistsError(f"Already exists: {target}")
    target.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding="utf-8")
    print(f"Created {target}")

def main():
    p=argparse.ArgumentParser(description="Create a vocabulary or sentence post.")
    sub=p.add_subparsers(dest="type",required=True)
    v=sub.add_parser("vocabulary"); v.add_argument("--number",type=int); v.add_argument("--title",default="New vocabulary chunk")
    s=sub.add_parser("sentence"); s.add_argument("--number",type=int); s.add_argument("--chapter",type=int,required=True); s.add_argument("--sentence",type=int,required=True)
    a=p.parse_args(); n=a.number or next_number()
    if a.type=="vocabulary":
        blank={"text":"","reading":None,"note":None}
        concepts=[]
        for _ in range(5): concepts.append({"english":"","chinese":blank.copy(),"japanese":{**blank,"kana":None},"german":blank.copy()})
        write(n,{"type":"vocabulary","number":n,"title":a.title,"subtitle":None,"concepts":concepts,"usage":[],"note":None})
    else:
        write(n,{"type":"sentence","number":n,"chapter":a.chapter,"sentence":a.sentence,"english":{"tokens":[{"text":""}]},"chinese":{"tokens":[{"text":"","reading":""}],"pattern":None,"observation":None},"japanese":{"tokens":[{"text":"","reading":"","kana":None}],"pattern":None,"observation":None},"german":{"tokens":[{"text":""}],"pattern":None,"observation":None},"connection":None,"field_note":None})
if __name__=="__main__": main()
