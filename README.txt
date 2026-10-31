おとなでも間違う日本の伝統・歴史  更新手順

■ ファイルの構成
  data/items.json      全項目(ここを直すのが基本)
  data/sources.json    出典の一覧(ID → 種別・題名・URL)
  data/glossary.json   用語集(語 → 読み・説明)
  data/changelog.json  訂正・更新履歴(ページに表示される)
  config/site.json     サイト名・公開URL(base_url)・リポジトリURL(repo_url)
  template/            ページの雛形
  build.py             上のデータからdocs/を作るスクリプト
  docs/                公開されるファイル(build.pyが作る。直接は直さない)

■ 項目を足す・直す手順
  1. data/items.json に項目を追加、または既存項目を直す。
     必須: id, name, era, type, claim_form, fields, plain_summary, established,
           claim_code(C/P/N), claim_note, actors, confidence, source_ids, caveats, last_checked
  2. 新しい出典は data/sources.json に追加(IDは重ならないように。例 F01)。
     URLは、実際に開いて確認できたものだけを書く。
  3. data/changelog.json の先頭に、変更日と内容(と対象のID)を1行足す。
  4. ターミナルで  python3 build.py  を実行。
     → 検証に通らないと止まり、理由が表示される(IDの重複、未登録の出典、
       「確認済」なのに出典が2件未満、など)。
  5. docs/ の中身をコミットして公開(下記)。

■ 確度の付け方(サイトの定義と同じ)
  確認済 : 複数の独立した出典で一致(辞典の集約は1系統として数える)
  要確認 : 出典が1系統、本文未読、または見解が分かれる
  確認不可: 検索では裏づけが得られなかった
  変わりうる情報(法律・研究・情勢)は、last_checked を更新したときだけ日付を変える。

■ 公開(GitHub Pages)
  1. GitHubで新しいリポジトリを作り、このフォルダ一式をアップロードする。
  2. リポジトリの Settings → Pages で、公開元を「main ブランチ / docs フォルダ」にする。
  3. 公開URLが決まったら config/site.json の base_url に入れる
     (例 https://アカウント名.github.io/リポジトリ名)。repo_url にもリポジトリのURLを入れる。
  4. python3 build.py を再実行し、docs/ をコミットする。
     (robots.txt・sitemap.xml・llms.txt のURLが __BASE_URL__ のままの間は、
      検索エンジン向けの案内として機能しない)
  5. リポジトリの Settings → Features で Issues を有効にすると、
     誤りの指摘の受付窓口になる。

■ 注意
  - GitHub Pagesは、公開サイト1GBまで、帯域は月100GBの目安(ソフト制限)。2026-10-25時点の公式の記載。
    変わりうるので、公開前に公式ページで再確認する。
  - llms.txt は提案段階のもので、正式な標準ではない。補助として置いている。
  - 出典の文章は、長く引用せず、要点を自分の言葉で書く。
