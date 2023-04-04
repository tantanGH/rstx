# RSTX

RS232C Binary File Transfer Tool for Python and X680x0/Human68k

---

### About This

これは RS232C クロス接続した相手の X680x0/PC/Mac/Linux にファイルを送信するためのプログラムです。 
Python汎用版とX680x0/Human68k版がそれぞれ用意されています。

相手方には [RSRX](https://github.com/tantanGH/rsrx/) を導入してセットで使います。

MOメディアなどでのやりとりと異なり、ファイル名を大文字8+3に変更する必要がありません。長いファイル名も小文字もそのまま転送できます。
タイムスタンプも維持されます。ただし18+3文字まで、日本語は非対応です。

---

### Install (Python版)

    pip install git+https://github.com/tantanGH/rstx.git

[Windowsユーザ向けPython導入ガイド](https://github.com/tantanGH/distribution/blob/main/windows_python_for_x68k.md)

---

### Install (X680x0/Human68k版)

RSTXxxx.ZIP をダウンロードして展開し、RSTX.X をパスの通ったディレクトリに置きます。

また、高速RS232Cドライバとして TMSIO.X を推奨します。

http://retropc.net/x68000/software/system/rs232c/tmsio/

X68000 LIBRARY からダウンロードして導入しておきます。


Human68k 3.02付属のRSDRV.SYSを組み込んだ場合は19200bpsまでの通信が可能です。

なお、本ソフトウェアは TMSIO.X を改造した BSIO.X には対応してません。(ハードウェアフロー制御固定となっているため)

---

### 使い方

    usage: rstx [-h] [--device DEVICE] [-s BAUDRATE] [-c CHUNK_SIZE] [-t TIMEOUT] files [files ...]

`--device` (Python版のみ) RS232Cポートのデバイス名を指定します。Windowsであれば `COM1` みたいな奴です。Macで USB-RS232C ケーブルを使っている場合は `/dev/tty.usbserial-xxxx` みたいになります。デフォルトで入っているのは我が家のMacのデバイス名ですw

`-s` で通信速度を指定します。相手方の RSRX での設定値に合わせてあげる必要があります。

`-c` でチャンクサイズを変更できます。データはこの単位に分割されて送信され、その都度CRCチェックが行われます。デフォルトは8KBです。

`-t` でタイムアウト(秒)を設定します。

その後に送信したいファイル名を指定します。複数ファイルを同時に指定することも可能です。
ただ、所詮RS232Cなのであまり大きいファイル(数十MBとか)はお勧めしません。MOなど別の手段を考慮した方が良いと思います。
