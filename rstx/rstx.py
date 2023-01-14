import argparse
import os
import serial
import binascii

def transfer_files(files, device, speed, chunk_size, timeout):

  port = serial.Serial( device, speed, timeout=timeout )

  for file in files:

    transfer_file_size = os.path.getsize(file)

    basename_and_ext = os.path.splitext(os.path.basename(file))
    basename = basename_and_ext[0]
    extname = basename_and_ext[1]
    if len(basename) > 18:
      basename = basename[:18]
      print(f"*** base file name is exceeding 18 chars. trimmed as f{basename}")

    if len(extname) > 0:
      extname = "." + extname
    
    transfer_file_name = (basename + extname + "                                ")[:32]

    print(f"Transferring [{file}] as [{transfer_file_name}] / [{transfer_file_size} bytes]")

    port.write(b"RSTX0000")
    port.write(transfer_file_size.to_bytes(4,'big'))
    port.write(transfer_file_name.encode('cp932'))

    with open(file, "rb") as f:
      chunk_data = f.read( chunk_size )
      while chunk_data:
        chunk_len  = len( chunk_data )
        chunk_crc  = binascii.crc32( chunk_data, 0 )
        print(f"chunk length={chunk_len},crc={chunk_crc}")

        port.write(chunk_len.to_bytes(4,'big'))
        port.write(chunk_data)
        port.write(chunk_crc.to_bytes(4,'big'))
        
        ack = port.read_all()
        print(ack)
 
    port.write(b"RSTXDONE")
    port1.close()

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("files", help="transfer files", nargs='+')
    parser.add_argument("-d","--device", help="serial device name", default='/dev/tty.usbserial-AQ028S08')
    parser.add_argument("-s","--speed", help="baud rate", type=int, default=38400)
    parser.add_argument("-c","--chunk_size", help="chunk size", type=int, default=65535)
    parser.add_argument("-t","--timeout", help="time out[sec]", type=int, default=600)

    args = parser.parse_args()

    transfer_files(args.files, args.device, args.speed, args.chunk_size, args.timeout)


if __name__ == "__main__":
    main()
