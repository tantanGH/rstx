import argparse
import os
import datetime
import time
import serial
import binascii

def read_in_chunks(file_object, chunk_size):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def transfer_files(files, device, speed, chunk_size, timeout, wait):

  port = serial.Serial( device, speed,
                        bytesize = serial.EIGHTBITS,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        timeout = timeout,
                        xonxoff = False,
                        rtscts = True,
                        dsrdtr = False )

  for file in files:

    transfer_file_size = os.path.getsize(file)
    transfer_file_time = str(datetime.datetime.fromtimestamp(os.path.getmtime(file)))[:19]

    basename_and_ext = os.path.splitext(os.path.basename(file))
    basename = basename_and_ext[0]
    extname = basename_and_ext[1]
    if len(basename) > 18:
      basename = basename[:18]
      print(f"*** base file name is exceeding 18 chars. trimmed as f{basename}")
    
    transfer_file_name = (basename + extname + "                                ")[:32]

    print(f"Transferring [{file}] as [{transfer_file_name}] / [{transfer_file_size} bytes]")

    # open port
    if port.isOpen() is False:
      port.open()
    
    # discard current input
    #port.read_all()

    # header 80 bytes
    port.write(b"RSTX7650")                             #  8 bytes
    port.write(transfer_file_size.to_bytes(4,'big'))    #  4 bytes
    port.write(transfer_file_name.encode('cp932'))      # 32 bytes
    port.write(transfer_file_time.encode('ascii'))      # 19 bytes
    port.write(b".................")                    # 17 bytes

    # initial crc
    crc = 0

    with open(file, "rb") as f:

      for chunk_data in read_in_chunks(f, chunk_size):

        chunk_len  = len( chunk_data )
        chunk_crc  = binascii.crc32( chunk_data, crc )
        print(f"chunk length={chunk_len},crc={chunk_crc}")

        port.write(chunk_len.to_bytes(4,'big'))         # 4 bytes
        port.write(chunk_data)                          # chunk_len bytes
        port.write(chunk_crc.to_bytes(4,'big'))         # 4 bytes
   
        crc = chunk_crc

      last_chunk_size = 0
      port.write(last_chunk_size.to_bytes(4,'big'))       # 4 bytes

#    port.close()
    time.sleep(wait)

  # closing eye catch
  if port.isOpen() is False:
    port.open()
  port.write(b"RSTXDONE")
  port.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("files", help="transfer files", nargs='+')
    parser.add_argument("-d","--device", help="serial device name", default='/dev/tty.usbserial-AQ028S08')
    parser.add_argument("-s","--baudrate", help="baud rate", type=int, default=19200)
    parser.add_argument("-c","--chunk_size", help="chunk size", type=int, default=8192)
    parser.add_argument("-t","--timeout", help="time out[sec]", type=int, default=180)
    parser.add_argument("-w","--wait", help="wait time[sec]", type=int, default=10)

    args = parser.parse_args()

    transfer_files(args.files, args.device, args.baudrate, args.chunk_size, args.timeout, args.wait)


if __name__ == "__main__":
    main()
