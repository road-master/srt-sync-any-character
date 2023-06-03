# SrtSync Any Character

[SrtSync] が文字化けする問題を解決するためのツールです  
[SrtSync] は AviUtl で動画に行ったカット編集と同じように字幕をカットするツールです

## インストール

1\.  
Windows に Python をインストールします:

```powershell
choco install -y python
```

2\.  
このリポジトリーから `srt_sync.py` をダウンロードします

3\.  
[DTV補完所] ー＞DTV から `SrtSync0.1.9` をダウンロードし、  
`srt_sync.py` と同じフォルダに `SrtSync.exe` を配置します

4\.  
[AviUtlプラグイン置き場] にある `自動フィールドシフト インタレース解除プラグイン ver7.5a` をダウンロードし、  
[AviUtl] に `del_import.auf` をインストールします

参考: [AviUtlと拡張編集プラグインの導入方法【ダウンロード･インストール】 | AviUtlの易しい使い方](https://aviutl.info/dl-innsuto-ru/)

## 使い方

1\.  
AviUtl でカット編集前の ts ファイルから字幕を抽出します:

```powershell
ffmpeg -fix_sub_duration -i original.ts -c:s text sub.srt
```

2\.  
AviUtl でカット編集します

3\.  
AviUtl から削除リストをエクスポートします:

[ファイル] -> [エクスポート] -> [削除リスト]

4\.  
削除リストと字幕を srt_sync.py に渡します:

```powershell
python srt_sync.py remove_list.txt sub.srt
```

すると、カットされた字幕が出力されます

5\.  
AviUtl でカット編集後の mp4 ファイルに字幕を合成します:

```powershell
ffmpeg -i cut.mp4 -i sub_cut.srt -c copy -c:s mov_text -metadata:s:s:0 language=jpn subtitled.mp4
```

[SrtSync]: http://www2.wazoku.net/2sen/
[DTV補完所]: http://www2.wazoku.net/2sen/
[AviUtlプラグイン置き場]: https://aji0.web.fc2.com/
[AviUtl]: http://spring-fragrance.mints.ne.jp/aviutl/
