# ============================================
# GPX → 平面直交座標系9系 CSV変換ツール
# Version: 0.0.0
#
# 概要:
#   GUIベース初期実装（PySide6）
#   最低限のUIと変換処理を統合
#
# 今後の拡張予定:
#   - スレッド化（UIフリーズ防止）
#   - D&D対応
#   - ログ詳細化
#   - エラーハンドリング強化
#   - 設定保存（ini/json）
#
# 変更履歴:
# --------------------------------------------
# v0.0.0 (2026-03-29)
#   - 初期GUI実装
#   - ファイル選択
#   - アンテナ高入力
#   - CSV出力（基本動作）
# --------------------------------------------
# ============================================

import sys
import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QFileDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QMessageBox, QProgressBar
)

from PySide6.QtCore import Qt

from pyproj import Transformer


# ============================================
# コア処理
# ============================================

def convert_gpx_to_csv(input_gpx, antenna_height, log_callback=None, progress_callback=None):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:6677", always_xy=True)

    tree = ET.parse(input_gpx)
    root = tree.getroot()

    ns = {}
    if root.tag.startswith("{"):
        ns_uri = root.tag.split("}")[0].strip("{")
        ns = {"gpx": ns_uri}
        wpt_path = "gpx:wpt"
        ele_path = "gpx:ele"
        name_path = "gpx:name"
        time_path = "gpx:time"
    else:
        wpt_path = "wpt"
        ele_path = "ele"
        name_path = "name"
        time_path = "time"

    wpts = root.findall(wpt_path, ns)

    if len(wpts) == 0:
        raise ValueError("waypointが存在しない")

    rows = []
    total = len(wpts)

    for i, wpt in enumerate(wpts):
        lat = float(wpt.get("lat"))
        lon = float(wpt.get("lon"))

        ele = wpt.find(ele_path, ns)
        name = wpt.find(name_path, ns)
        time_elem = wpt.find(time_path, ns)

        raw_z = float(ele.text) if ele is not None else 0.0
        z = raw_z - antenna_height

        name_text = name.text if (name is not None and name.text) else f"P{i+1:03d}"

        if log_callback:
            log_callback(f"処理中: {name_text}")

        date_str = ""
        if time_elem is not None and time_elem.text:
            try:
                dt = datetime.fromisoformat(time_elem.text.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y%m%d")
            except:
                date_str = ""

        try:
            x, y = transformer.transform(lon, lat)
        except Exception:
            raise RuntimeError(f"座標変換失敗: {name_text}")

        rows.append([name_text, x, y, z, antenna_height, date_str])

        if progress_callback:
            progress_callback(int((i + 1) / total * 100))

    base_name = os.path.splitext(os.path.basename(input_gpx))[0]
    output_csv = os.path.join(os.path.dirname(input_gpx), base_name + ".csv")

    if os.path.exists(output_csv):
        raise FileExistsError("出力ファイルが既に存在する")

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["CODE", "X", "Y", "Z", "ANTENNA_HEIGHT", "DATE"])
        writer.writerows(rows)

    return output_csv


# ============================================
# GUI
# ============================================

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPX → CSV 変換ツール")

        self.file_path = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # ファイル選択
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setReadOnly(True)
        btn_browse = QPushButton("参照")
        btn_browse.clicked.connect(self.select_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(btn_browse)

        # アンテナ高
        antenna_layout = QHBoxLayout()
        self.antenna_edit = QLineEdit("1.8")
        antenna_layout.addWidget(QLabel("アンテナ高 (m)"))
        antenna_layout.addWidget(self.antenna_edit)

        # ボタン
        btn_layout = QHBoxLayout()
        self.btn_execute = QPushButton("実行")
        self.btn_execute.clicked.connect(self.execute)
        self.btn_execute.setEnabled(False)

        btn_exit = QPushButton("終了")
        btn_exit.clicked.connect(self.close)

        btn_layout.addWidget(self.btn_execute)
        btn_layout.addWidget(btn_exit)

        # プログレス
        self.progress = QProgressBar()

        # ログ
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout.addLayout(file_layout)
        layout.addLayout(antenna_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress)
        layout.addWidget(self.log)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "GPX選択", "", "GPX Files (*.gpx)")
        if file_path:
            self.file_path = file_path
            self.file_edit.setText(file_path)
            self.validate_inputs()

    def validate_inputs(self):
        try:
            float(self.antenna_edit.text())
            valid = bool(self.file_path)
        except:
            valid = False

        self.btn_execute.setEnabled(valid)

    def log_message(self, msg):
        self.log.append(msg)

    def set_progress(self, value):
        self.progress.setValue(value)

    def execute(self):
        try:
            antenna_height = float(self.antenna_edit.text())

            output = convert_gpx_to_csv(
                self.file_path,
                antenna_height,
                log_callback=self.log_message,
                progress_callback=self.set_progress
            )

            QMessageBox.information(self, "完了", f"出力完了:\n{output}")

        except FileExistsError:
            QMessageBox.warning(self, "警告", "出力ファイルが既に存在します")

        except Exception as e:
            QMessageBox.critical(self, "エラー", str(e))


# ============================================
# エントリポイント
# ============================================

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()