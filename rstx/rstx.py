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
                        rtscts = False,
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

    print("--")
    print(f"Transferring [{file}] as [{transfer_file_name}] / [{transfer_file_size} bytes]")

    # open port
    if port.isOpen() is False:
      port.open()
    
    # discard current input
    #port.read_all()

    # header 16 + 80 bytes
    port.write(b"                                ")     # 16 bytes (dummy)
    port.write(b"RSTX7650")                             #  8 bytes
    port.write(transfer_file_size.to_bytes(4,'big'))    #  4 bytes
    port.write(transfer_file_name.encode('cp932'))      # 32 bytes
    port.write(transfer_file_time.encode('ascii'))      # 19 bytes
    port.write(b".................")                    # 17 bytes
    time.sleep(3)

    # wait response
    while port.in_waiting < 4:
      pass

    # ack 
    ack = port.read_all()
    if b"LINK" not in ack:
      print("Failed to establish link.")
      port.close()
      return

    # initial crc
    crc = 0

    # total size
    total_size = 0

    # abort flag
    abort = False

    with open(file, "rb") as f:

      for chunk_data in read_in_chunks(f, chunk_size):

        chunk_len  = len( chunk_data )
        chunk_crc  = binascii.crc32( chunk_data, crc )

        for retry in range(3):

          port.write(chunk_len.to_bytes(4,'big'))         # 4 bytes
          port.write(chunk_data)                          # chunk_len bytes
          port.write(chunk_crc.to_bytes(4,'big'))         # 4 bytes
   
          while port.in_waiting < 4:
            pass

          ack = port.read(4)
          if ack == b"EXIT":
            abort = True
            break 
          elif ack == b"PASS":
            crc = chunk_crc
            total_size += chunk_len
            print(f"\rSent {total_size} bytes. (CRC={chunk_crc:08X})", end="")
            break
         
          print(f" Retry. ({retry+1}/3)")              

        if abort:
          break

      last_chunk_size = 0
      port.write(last_chunk_size.to_bytes(4,'big'))       # 4 bytes

      print("\nTransfer completed.")

    time.sleep(wait)

    # wait response
    while port.in_waiting < 4:
      pass

    # ack
    ack = port.read(4)
    if ack != b"DONE":
      print("Failed to get success ack.")
      port.close()
      return

  # closing eye catch
  if port.isOpen() is False:
    port.open()
  port.write(b"RSTXDONE")

  time.sleep(wait*3)
  port.close()

  print("--")
  print("Closed communication.")

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("files", help="transfer files", nargs='+')
    parser.add_argument("--device", help="serial device name", default='/dev/tty.usbserial-AQ028S08')
    parser.add_argument("-s","--baudrate", help="baud rate", type=int, default=19200)
    parser.add_argument("-c","--chunk_size", help="chunk size", type=int, default=8192)
    parser.add_argument("-t","--timeout", help="time out[sec]", type=int, default=180)
    parser.add_argument("-w","--wait", help="wait time[sec]", type=int, default=3)

    args = parser.parse_args()

    transfer_files(args.files, args.device, args.baudrate, args.chunk_size, args.timeout, args.wait)


if __name__ == "__main__":
    main()
