import json
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-u","--update",action="store_true",dest="update",default=False)
parser.add_option("-a","--author",dest="author_party",default=None)
parser.add_option("-l","--link",action="store_true",dest="use_link",default=False)
options,args = parser.parse_args()
if options.update:
    import requests
    print("Starting download...")
    full_data = requests.get("https://app.parlamento.pt/webutils/docs/doc.txt?path=6148523063446f764c324679626d56304c3239775a57356b595852684c3052685a47397a51574a6c636e52766379394a626d6c6a6157463061585a68637939595356596c4d6a424d5a57647063327868644856795953394a626d6c6a6157463061585a686331684a566c3971633239754c6e523464413d3d&fich=IniciativasXIV_json.txt&Inline=true").text
    open("./data.json","w").write(full_data)
    print("Done!")
    full_data = json.loads(full_data)
else:
    full_data = json.loads(open("./data.json","r").read())

full_data = full_data["ArrayOfPt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut"]["pt_gov_ar_objectos_iniciativas_DetalhePesquisaIniciativasOut"]
polls = []
useful = [250,310,320,335]

def first_or_self(obj):
    if isinstance(obj,list):
        return obj[0]
    else:
        return obj

for i in full_data:
    events = i["iniEventos"]["pt_gov_ar_objectos_iniciativas_EventosOut"]
    if isinstance(events,list):
        for e in events:
            if "votacao" in e and int(e["codigoFase"]) in useful and "detalhe" in e["votacao"]["pt_gov_ar_objectos_VotacaoOut"]:
                # print(i["iniTitulo"] + ": " + e["votacao"]["pt_gov_ar_objectos_VotacaoOut"]["detalhe"])
                # print(i)
                author = first_or_self(i["iniAutorGruposParlamentares"]["pt_gov_ar_objectos_AutoresGruposParlamentaresOut"])["GP"] if "iniAutorGruposParlamentares" in i else (first_or_self(i["iniAutorDeputados"]["pt_gov_ar_objectos_iniciativas_AutoresDeputadosOut"])["nome"] if "iniAutorDeputados" in i else first_or_self(i["iniAutorOutros"]["nome"]))

                pre_votes = e["votacao"]["pt_gov_ar_objectos_VotacaoOut"]["detalhe"]
                pre_votes = pre_votes.replace("<I>","").replace("</I>","").split("<BR>")
                votes = {"for":None,"against":None,"absent":None}
                for a in pre_votes:
                    # print(a)
                    tmp_votes = list(map(lambda b: b.strip(),a.split(":")[1].split(",")))
                    if a.startswith("A Favor"):
                        votes["for"] = tmp_votes
                    elif a.startswith("Contra"):
                        votes["against"] = tmp_votes
                    elif a.startswith("Abstenção"):
                        votes["absent"] = tmp_votes

                polls.append({"title":i["iniTitulo"],
                    "id":e["votacao"]["pt_gov_ar_objectos_VotacaoOut"]["id"],
                    "votes":votes,
                    "url":i["iniLinkTexto"],
                    "date":e["votacao"]["pt_gov_ar_objectos_VotacaoOut"]["data"],
                    "author":author})


if options.author_party:
    polls = list(filter(lambda a: a["author"] == options.author_party,polls))


for p in sorted(polls,key=lambda a:a["id"]):
    print("\n")
    print(p["title"])
    # print(" ", p["id"])
    print(" ", p["author"])
    print(" ", p["date"])
    if options.use_link:
        print(" ", p["url"])
    print(" ","For:", str(p["votes"]["for"]))
    print(" ","Against:", str(p["votes"]["against"]))
    print(" ","Absent:", str(p["votes"]["absent"]))
