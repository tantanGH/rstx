# rstx

RS232C Binary File Transfer Tool in Python

---

## About This

これは RS232C クロス接続した相手の X680x0 にファイルを送信するためのプログラムです。 
相手方には [RSRX.X](https://github.com/tantanGH/rsrx/) を導入してセットで使います。

---

## Install

    pip install git+https://github.com/tantanGH/rstx.git

[Windowsユーザ向けPython導入ガイド](https://github.com/tantanGH/distribution/blob/main/windows_python_for_x68k.md)

---

## Usage

    usage: rstx [-h] [-d DEVICE] [-s BAUDRATE] [-c CHUNK_SIZE] [-t TIMEOUT] files [files ...]

`-d` でRS232Cポートのデバイス名を指定します。Windowsであれば `COM1` みたいな奴です。Macで USB-RS232C ケーブルを使っている場合は `/dev/tty.usbserial-xxxx` みたいになります。デフォルトで入っているのは我が家のMacのデバイス名ですw

`-s` で通信速度を指定します。相手方の RSRX.X での設定値に合わせてあげる必要があります。

`-c` でチャンクサイズを変更できます。データはこの単位に分割されて送信され、その都度CRCチェックが行われます。デフォルトは8KBです。

`-t` でタイムアウト(秒)を設定します。

その後に送信したいファイル名を指定します。複数ファイルを同時に指定することも可能です。
ただ、所詮RS232Cなのであまり大きいファイル(数十MBとか)はお勧めしません。MOなど別の手段を考慮した方が良いと思います。

---

## Mac で USB - RS232C 変換ケーブルを選ぶ際の注意点

USB - RS232C 変換ケーブルはネットワーク機器や制御機器との接続のために一定の需要があり、入手性はとても良く、値段も1000円台からあり安価です。
ただし、使われているチップセットによって最近の macOS ではうまく認識されず `/dev/tty.usbserial-*` が出てこない場合があります。

我が家でうまくいかなかったケーブルの例 (Prolificチップセット)
- https://www.amazon.co.jp/gp/product/B00QUZY4UG/

我が家でうまくいったケーブルの例 (FTDIチップセット)
- https://www.amazon.co.jp/gp/product/B07589ZF9X/

なお、Mac対応と謳われていたり、Mac用のドライバが付属していたりすることもありますが、基本的に macOS 11以上であればドライバ不要です。
セキュリティの都合で macOS のデバイスドライバの仕組みが変わりつつありますので、古いデバイスドライバを導入してしまう前にまずは一度接続して `/dev/tty.usbserial-*` の存在を確認してみてください。