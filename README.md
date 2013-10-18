MapProxy Plugin for QGIS
======================
このプログラムは、地図タイル形式の画像をQGISで表示するためのプラグインです。
MapProxyをローカルPCにインストールして、それをwmsレイヤーとしてQGISから読み込むことによって地図タイルを表示します。
あらかじめ、電子国土背景地図、エコリス地図タイルをプリセットしているので（予定）、これらの地図をQGISで簡単に表示できます。
また、MapProxyの設定ファイルを編集することによって独自の地図タイルを追加することもできます。
なお、MapProxyはVirtualenv上にインストールするので、各自のpython環境は汚しません。

使い方 (現在テスト中につき、プラグインのインストールは手動でお願いします。)
------
1. 以下からプログラムをダウンロードしてください。https://github.com/tmizu23/mapproxy_plugin/archive/custom_jp.zip
2. 解凍したのち、フォルダ名を「mapproxy_plugin」に変更してください。それをQGISプラグインのフォルダに入れてください。($HOME/.qgis2/python/plugins/) 
3. QGIS(バージョン2.0以上)を起動させます。
4. プラグインメニューから「MapProxy Plugin」を有効にします。
5. プラグインメニュー --> MapProxy plugin --> Installl Mapproxy を選択してMapproxyをインストールします。この作業は最初の1回だけ必要です。
6. プラグインメニュー --> MapProxy plugin -->　Run MapProxy を選択してMapproxyを起動します。問題がなければ、設定ファイルが読み込まれます。
7. プラグインメニュー --> MapProxy plugin　から追加したレイヤーを選択して地図に表示させます。

※ プリセットしている地図タイルの制限により、このプラグインの起動中はQGISの印刷機能が制限されます。（プリンタへの出力不可、PDFおよび画像への出力はA4のみ）

地図設定（上級者向け）
------
MapProxyの設定ファイル(yaml)を編集追加することによって、独自の地図タイルを追加することができます。

1. 以下のサイトを参考にyamlファイルを作成します。 http://mapproxy.org/docs/nightly/index.html
2. yamlファイルをQGISプラグインの中の「project」フォルダに入れてください。 例(~/.qgis2/python/plugins/mapproxy_plugin/project/) 

yamlファイルに関する制限  
- "services"に"wms"を追加する必要があります。
- "services"-->"wms"-->"srs"を設定する必要があります。例 srs: ['EPSG:4326']


ライセンスおよび注意事項
----------
- このプログラムは MITライセンスに従います。
- このプログラムを利用して読み込む地図タイル等は、それらのデータを配信する各サービスの規約に従ってください。
- プリセットしている「電子国土背景地図等データ」を利用の際は、次の規約に同意の上、それに従ってください。http://portal.cyberjapan.jp/portalsite/kiyaku/
- プリセットしている「エコリス地図タイル」を利用の際は、次の規約に同意の上、それに従ってください。http://map.ecoris.info

