# gpx2csvGUI
Python script

GPXファイルのwaypointを読み込み、平面直角座標系（9系）へ変換しCSVとして出力するGUIツール。
ご使用いただくのは自由で構いませんが、私の個人用ツールとして作ったものですので動作の保証や動作したことによる損害への補償は一切いたしません。
---

## 概要

* 入力：GPXファイル
* 出力：CSVファイル（同一ディレクトリ）
* 座標系変換：

  * 入力：WGS84（EPSG:4326）
  * 出力：平面直角座標系9系（EPSG:6677）

---

## 動作環境

* Python 3.12
* Windows 10 / 11

---

## セットアップ

仮想環境を作成し、依存パッケージをインストールする。

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 実行（開発環境）

```bash
python main.py
```

---

## ビルド手順（PyInstaller）

### 1. PyInstallerインストール

```bash
pip install pyinstaller
```

---

### 2. クリーン

```powershell
Remove-Item build, dist -Recurse -Force -ErrorAction Ignore
Remove-Item gpx2csv.spec -ErrorAction Ignore
```

---

### 3. ビルド実行

```bash
python -m PyInstaller main.py ^
  --name gpx2csv ^
  --onedir ^
  --noconsole ^
  --collect-all PySide6 ^
  --collect-all pyproj
```

---

### 4. ビルド成果物

```text
dist/
 └─ gpx2csv/
     ├─ gpx2csv.exe
     └─ _internal/
```

---

## 配布方法

**dist/gpx2csv フォルダをそのまま配布すること**

### 注意

* exe単体では動作しない
* `_internal` フォルダは必須

---

## 使用方法

1. アプリ起動
2. GPXファイルを選択
3. アンテナ高を入力
4. 実行ボタン押下

---

## 出力仕様

CSV形式：

```text
CODE,X,Y,Z,ANTENNA_HEIGHT,DATE
```

---

## エラー仕様

* 出力ファイルが既に存在する場合は停止
* waypointが存在しない場合はエラー

---

## バージョン

* v1.0.0

---

## ライセンス

未定（必要に応じて追記）
