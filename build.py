# -*- coding: utf-8 -*-
"""data/ と config/ から docs/ を生成する。使い方: python3 build.py"""
import json, html as _h, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def J(p): return json.load(open(ROOT/p,encoding="utf-8"))
esc=_h.escape
RAW=J("data/items.json"); SRC={k:tuple(v) for k,v in J("data/sources.json").items()}
GLD=J("data/glossary.json"); GL={k:(v["reading"],v["meaning"]) for k,v in GLD.items()}
CHG=J("data/changelog.json"); CFG=J("config/site.json")
PLAIN={r["id"]:r["plain_summary"] for r in RAW}
CHK={r["id"]:r["last_checked"] for r in RAW}
TYPE={"S":"近代の創作","G":"外来・移民の歴史","R":"宗教史の流れ","Z":"制度の経緯","K":"戦争の記録","L":"地域でちがう"}
TNAME_TO_K={v:k for k,v in TYPE.items()}
OVR={"M03":"R","M09":"Z","M10":"Z","M11":"Z","M12":"Z","M13":"Z","W05":"G"}
FORM_OVR={"W05":"固有・純粋型"}
ERAS=[("古代","〜1185"),("中世","1185–1573"),("近世","1573–1868"),("明治","1868–1912"),("大正","1912–1926"),("昭和初期","1926–1937"),("昭和戦中","1937–1945"),("昭和戦後","1945–1989"),("平成以降","1989–"),("年代不明","時期を確認できず")]
ERA_CLS={"古代":"e7","中世":"e8","近世":"e9","明治":"e1","大正":"e2","昭和初期":"e3","昭和戦中":"e4","昭和戦後":"e5","平成以降":"e6","年代不明":"e10"}
ERA_RANGE=dict(ERAS); ORDER={e:i for i,(e,_) in enumerate(ERAS)}
CONF_CLS={"確認済":"ok","要確認":"warn","確認不可":"ng"}
CLAIM={"C":"出典で確認","P":"間接・部分的","N":"未確認"}
FIELDS=["マナー","習慣","歴史","文化","宗教"]

# ---- 検証(誤りがあれば止める) ----
def validate():
    errs=[]; ids=set()
    for r in RAW:
        i=r["id"]
        if i in ids: errs.append(f"{i}: IDが重複")
        ids.add(i)
        if r["era"] not in ORDER: errs.append(f"{i}: 不明な年代 {r['era']}")
        if r["type"] not in TYPE.values(): errs.append(f"{i}: 不明な系統 {r['type']}")
        if r["confidence"] not in CONF_CLS: errs.append(f"{i}: 不明な確度 {r['confidence']}")
        if r["claim_code"] not in CLAIM: errs.append(f"{i}: 不明な古来の主張コード {r['claim_code']}")
        for f in r["fields"]:
            if f not in FIELDS: errs.append(f"{i}: 不明な分野 {f}")
        for s in r["source_ids"]:
            if s not in SRC: errs.append(f"{i}: 出典 {s} が sources.json にない")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",r["last_checked"]): errs.append(f"{i}: last_checked の形式が不正")
        if r["confidence"]=="確認済" and len(r["source_ids"])<2: errs.append(f"{i}: 確認済なのに出典が2件未満")
        if not r["plain_summary"].strip(): errs.append(f"{i}: plain_summary が空")
    for s,v in SRC.items():
        if not v[2].startswith("http"): errs.append(f"出典 {s}: URLが不正")
    if errs: print("\n".join(errs)); sys.exit("検証に失敗しました")
validate()
ITEMS=[(r["id"],r["era"],r["name"],r["fields"],r["established"],r["claim_code"],r["claim_note"],r["actors"],r["confidence"],
        " ".join(r["source_ids"]),r["caveats"],r["type"],r["claim_form"]) for r in RAW]
ITEMS.sort(key=lambda t:ORDER[t[1]])
LAST=max([r["last_checked"] for r in RAW]+[c["date"] for c in CHG])
BASE=(CFG.get("base_url") or "").rstrip("/")
arts=[];jitems=[]
for (iid,era,name,flds,est,cc,ctext,actor,conf,srcs,cav,typ,form) in ITEMS:
    sl=[s for s in srcs.split() if s in SRC]
    srch="".join(f'<li><span class="sid">{s}</span> <span class="stype">{esc(SRC[s][0])}</span> <a href="{esc(SRC[s][2])}" target="_blank" rel="noopener noreferrer">{esc(SRC[s][1])}</a></li>' for s in sl)
    arts.append(f'''<details class="card {ERA_CLS[era]}" id="{iid}" data-era="{era}" data-type="{typ}" data-fields="{' '.join(flds)}" data-claim="{cc}" data-conf="{conf}">
<summary><span class="cid">{iid}</span><span class="cmain"><span class="cname">{esc(name)}</span><span class="cplain">{esc(PLAIN[iid])}</span></span>
<span class="cbadges"><span class="b era">{era}</span><span class="b typ">{esc(typ)}</span><span class="b conf {CONF_CLS[conf]}">確度:{conf}</span><span class="b claim c{cc}">古来の主張:{CLAIM[cc]}</span></span></summary>
<div class="cbody"><dl>
<dt>系統</dt><dd>{esc(typ)}</dd>
<dt>分野</dt><dd>{esc('・'.join(flds))}</dd>
<dt>主張のかたち</dt><dd>{esc(form)}</dd>
<dt>成立時期と確認できた経緯</dt><dd>{esc(est)}</dd>
<dt>主張(出典で確認できた範囲)</dt><dd>{esc(ctext)}</dd>
<dt>担い手</dt><dd>{esc(actor)}</dd>
<dt>留保・反証・別の見方</dt><dd>{esc(cav)}</dd>
<dt>最終確認日</dt><dd>{CHK[iid]}</dd>
</dl><h4>出典</h4><ul class="srcs">{srch}</ul><p class="perma"><a href="#{iid}">この項目へのリンク #{iid}</a></p></div></details>''')
    jitems.append(dict(id=iid,name=name,type=typ,claim_form=form,era=era,era_range=ERA_RANGE[era],fields=flds,
        plain_summary=PLAIN[iid],established=est,antiquity_claim_status=CLAIM[cc],claim_note=ctext,actors=actor,
        confidence=conf,caveats=cav,last_checked=CHK[iid],sources=[dict(id=s,type=SRC[s][0],title=SRC[s][1],url=SRC[s][2]) for s in sl]))
n=len(ITEMS)
cnt_era={e:sum(1 for i in ITEMS if i[1]==e) for e,_ in ERAS}
cnt_f={f:sum(1 for i in ITEMS if f in i[3]) for f in FIELDS}
cnt_t={v:sum(1 for i in ITEMS if i[11]==v) for v in TYPE.values()}
n_claim=sum(1 for i in ITEMS if i[5]=="C" and i[8] in("確認済","要確認"))
cc_={c:sum(1 for i in ITEMS if i[8]==c) for c in("確認済","要確認","確認不可")}
THELP={"近代の創作":"明治以降に作られたのに、古くからあるように語られるものを見ます。","外来・移民の歴史":"「外から来たもの」と見られがちだが、長い歴史があるものを見ます。","宗教史の流れ":"神仏習合など、あまり語られない古くからの宗教の流れを見ます。","制度の経緯":"税や法律など、いまの制度に至るまでの経緯を見ます。","戦争の記録":"戦争中の出来事で、記録(公文書・裁判・研究)があるものを見ます。","地域でちがう":"「全国どこでも同じ」と思われがちだが、地域で違う作法や信仰を見ます。"}
type_tiles="".join(f'<button class="tile ty" data-set="type" data-val="{v}" data-help="{THELP[v]}"><span class="tt">{v}</span><span class="tn">{cnt_t[v]}<small>件</small></span></button>' for v in TYPE.values())
era_tiles="".join(f'<button class="tile {ERA_CLS[e]}" data-set="era" data-val="{e}" data-help="{e}({r})に始まった、または決められたものを見ます。"><span class="tt">{e}</span><span class="ts">{r}</span><span class="tn">{cnt_era[e]}<small>件</small></span></button>' for e,r in ERAS)
field_tiles="".join(f'<button class="tile f" data-set="field" data-val="{f}" data-help="{f}にかかわるものを見ます。1つの項目が複数の分野に入ることもあります。"><span class="tt">{f}</span><span class="tn">{cnt_f[f]}<small>件</small></span></button>' for f in FIELDS)
ld={"@context":"https://schema.org","@type":"Dataset","name":CFG["site_name"]+"データベース",
 "description":f"日本の「伝統」をめぐる思い込み({n}項目)。近代に作られたのに古来とされるもの、外来・移民の長い歴史、神仏習合などの宗教史、制度の経緯、戦争の記録を、出典・確度・反対の見方つきで整理したデータ。",
 "inLanguage":"ja","dateModified":LAST,"keywords":["創られた伝統","Invention of Tradition","神仏習合","渡来人","日本"]}
page=(ROOT/"template/site_template.html").read_text(encoding="utf-8")
for k,v in {"%%N%%":str(n),"%%NCLAIM%%":str(n_claim),"%%TYPE_TILES%%":type_tiles,"%%ERA_TILES%%":era_tiles,"%%FIELD_TILES%%":field_tiles,
  "%%CARDS%%":"\n".join(arts),"%%OK%%":str(cc_["確認済"]),"%%WARN%%":str(cc_["要確認"]),"%%NG%%":str(cc_["確認不可"]),
  "%%CHANGELOG%%":"".join(f'<li><b>{c["date"]}</b> {esc(c["summary"])}{(" ("+" ".join(c["ids"])+")") if c["ids"] else ""}</li>' for c in CHG),
  "%%CONTACT%%":(f'<a href="{esc(CFG["repo_url"])}/issues" rel="noopener noreferrer">{esc(CFG["repo_url"])}/issues</a>' if CFG.get("repo_url") else esc(CFG["contact_note"])),
  "%%LD%%":json.dumps(ld,ensure_ascii=False),
  "%%GLJSON%%":json.dumps(GL,ensure_ascii=False).replace("</","<\\/"),
  "%%GLLIST%%":"".join('<dt id="g-%s">%s<small>(%s)</small></dt><dd>%s</dd>'%(k,k,v[0],_h.escape(v[1])) for k,v in sorted(GL.items(),key=lambda kv:kv[1][0])),
  "%%JSON%%":json.dumps({"retrieved":LAST,"items":jitems},ensure_ascii=False).replace("</","<\\/")}.items():
    page=page.replace(k,v)
OUT=ROOT/"docs"; OUT.mkdir(exist_ok=True)
(OUT/"index.html").write_text(page,encoding="utf-8")
(OUT/"data.json").write_text(json.dumps({"retrieved":LAST,"glossary":GLD,"items":jitems},ensure_ascii=False,indent=1),encoding="utf-8")
(OUT/".nojekyll").write_text("",encoding="utf-8")
U=(BASE or "__BASE_URL__")
(OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {U}/sitemap.xml\n",encoding="utf-8")
(OUT/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{U}/</loc><lastmod>{LAST}</lastmod></url>\n  <url><loc>{U}/data.json</loc><lastmod>{LAST}</lastmod></url>\n</urlset>\n',encoding="utf-8")
llms=f"""# {CFG["site_name"]}

> 日本の「伝統」「歴史」をめぐる思い込み({n}項目)を、出典・確度・反対の見方つきで整理した参照データベース。近代に作られたのに古来とされるもの、外来・移民の長い歴史、神仏習合などの宗教史、制度の経緯、地域差、戦争の記録を扱う。最終更新: {LAST}。

引用するときは、項目ID・確度・最終確認日を添えてください。確度が「要確認」「確認不可」の項目は、断定の根拠にしないでください。分類(系統・主張のかたち)は本データベース独自の整理で、学説の定説ではありません。

## データ
- [data.json]({U}/data.json): 全項目(確度、出典URL、留保、最終確認日)と用語集(読み・説明)のJSON
- [一覧ページ]({U}/): 人間向けの一覧。項目へのリンクは #ID の形(例: {U}/#R02)

## 確度の読み方
- 確認済: 複数の独立した出典で一致
- 要確認: 出典が1系統、本文未読、または見解が分かれる
- 確認不可: 検索では裏付けが得られなかった

## Optional
- [訂正・更新履歴]({U}/#changelog): 変更の記録
"""
(OUT/"llms.txt").write_text(llms,encoding="utf-8")
if not BASE: print("警告: config/site.json の base_url が空です。robots.txt・sitemap.xml・llms.txt は __BASE_URL__ のままです。公開先が決まったら設定して再生成してください。")
print("OK",n,"items; last_checked",LAST,cc_,cnt_t)
