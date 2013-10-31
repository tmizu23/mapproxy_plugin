MapProxy Plugin for QGIS
======================
- このプログラムは、地図タイルをQGISで表示するためのプラグインです。
- MapProxy利用してを地図タイルをWMSとしてQGISに読み込みます。
- 地理院タイル、エコリス地図タイルをプリセットしています。
- MapProxyの設定ファイルを編集し独自の地図タイルを追加できます。

※ MapProxyはVirtualenv上にインストールするので、各自のpython環境は汚しません。

使い方
------
1. QGIS(バージョン2.0以上)を起動します。
2. プラグインメニュー --> 「プラグインの管理とインストール」--> 「設定」から http://map.ecoris.info/plugins.xml を追加します。
3. プラグインメニューから「MapProxy Plugin(custom_jp)」をインストールし、プラグインを有効にします。
4. プラグインメニュー --> MapProxy plugin --> Installl Mapproxy を選択してMapproxyをインストールします。この作業は最初の1回だけ必要です。
5. プラグインメニュー --> MapProxy plugin -->　Run MapProxy を選択してMapproxyを起動します。問題がなければ、設定ファイルが読み込まれます。
6. プラグインメニュー --> MapProxy plugin　から追加したレイヤーを選択して地図に表示させます。

※ このプラグインの起動中はQGISの印刷機能が制限されます。（プリンタへの出力不可、PDFおよび画像への出力はA3以下）

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
- プリセットしている「地理院タイル」を利用の際は、次の規約に同意の上、それに従ってください。http://portal.cyberjapan.jp/help/termsofuse.html
- プリセットしている「エコリス地図タイル」を利用の際は、次の規約に同意の上、それに従ってください。http://map.ecoris.info

