#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <fcntl.h>
#include <io.h>
#include <doslib.h>
#include <iocslib.h>
#include <zlib.h>
#include "memory.h"

#define VERSION "0.3.0"

inline static void* _doscall_malloc(size_t size) {
  uint32_t addr = MALLOC(size);
  return (addr >= 0x81000000) ? NULL : (void*)addr;
}

inline static void _doscall_mfree(void* ptr) {
  if (ptr == NULL) return;
  MFREE((uint32_t)ptr);
}

static void show_help() {
  printf("usage: rstx [options] <file>\n");
  printf("options:\n");
  printf("     -s <baud rate> (default:19200)\n");
  printf("     -c <chunk size> (default:8192)\n");
  printf("     -t <timeout[sec]> (default:120)\n");
  printf("     -h ... show version and help message\n");
}

static int32_t write_rs232c(uint8_t* buffer, size_t len, int32_t timeout) {

  int32_t rc = -1;

  uint32_t t0 = ONTIME();
  timeout *= 100;

  for (size_t i = 0; i < len; i++) {

    while (OSNS232C() == 0) {
      uint32_t t1 = ONTIME();
      if ((t1 - t0) > timeout) {
        printf("error: transfer timeout.\n");
        goto exit;
      }
    }

    OUT232C(buffer[i]);

  }

  rc = 0;

exit:
  return rc;
}

int32_t main(int32_t argc, uint8_t* argv[]) {

  // default exit code
  int32_t rc = -1;

  // program credit and version
  printf("RSTX.X - RS232C File Transfer Tool " VERSION " 2023 by tantan\n");
   
  // default parameters
  int32_t baud_rate = 19200;
  int16_t timeout = 120;
  int16_t chunk_size = 8192;
  size_t buffer_size = 128 * 1024;

  // data buffer
  uint8_t* chunk_data = NULL;

  // input file argument offset
  int16_t input_file_argc = -1;

  // input file handle
  FILE* fp = NULL;

  // command line options
  for (int16_t i = 1; i < argc; i++) {
    if (argv[i][0] == '-' && strlen(argv[i]) >= 2) {
      if (argv[i][1] == 's' && i+1 < argc) {
        baud_rate = atoi(argv[i+1]);
      } else if (argv[i][1] == 't' && i+1 < argc) {
        timeout = atoi(argv[i+1]);
      } else if (argv[i][1] == 'c' && i+1 < argc) {
        chunk_size = atoi(argv[i+1]);
      } else if (argv[i][1] == 'h') {
        show_help();
        goto exit;
      } else {
        printf("error: unknown option.\n");
        goto exit;
      }
    } else {
      input_file_argc = i;
      break;
    }
  }

  if (input_file_argc < 0) {
    printf("error: no input file.\n");
    goto exit;
  }

  // convert baud rate speed to IOCS SET232C() speed value
  int32_t speed = 8;
  switch (baud_rate) {
    case 9600:
      speed = 7;
      break;
    case 19200:
      speed = 8;
      break;
    case 38400:
      speed = 9;
      break;
    case 52080:
    case 57600:
      speed = 0x0d;
      break;
    case 76800:
    case 78125:
      speed = 0x0e;
      break;
    case 117180:
      speed = 0x0f;
      break;
    default:
    printf("error: unsupported baud rate.\n");
    goto exit;      
  }

  // setup RS232C port
  SET232C( 0x4C00 + speed );    // 8bit, non-P, 1stop, no-XON

  // buffer memory allocation
  chunk_data = _doscall_malloc(buffer_size);
  if (chunk_data == NULL) {
    printf("error: cannot allocate buffer memory.\n");
    goto exit;
  }

  // describe settings
  printf("--\n");
  printf("Baud Rate: %d bps\n", baud_rate);
  printf("Timeout: %d sec\n", timeout);
  printf("Buffer Size: %d KB\n", buffer_size);

  // file loop
  for (int16_t i = input_file_argc; i < argc; i++) {

    // check ESC key to exit
    if (B_KEYSNS() != 0) {
      int16_t scan_code = B_KEYINP() >> 8;
      if (scan_code == 0x01) {
        printf("\rCanceled.\x1b[0K\n");
        rc = 1;
        goto exit;
      }
    }

    uint8_t* input_file_name = argv[i];
    
    // input file attributes
    struct FILBUF filbuf;
    if (FILES(&filbuf, input_file_name, 0x20) < 0) {
      printf("error: cannot get file attributes for %s.\n", input_file_name);
      //goto exit;
      continue;
    }

    uint32_t transfer_file_size = filbuf.filelen;

    static uint8_t transfer_file_name[32+1];
    memset(transfer_file_name, ' ', 32);
    transfer_file_name[32] = '\0';
    memcpy(transfer_file_name, filbuf.name, strlen(filbuf.name));

    static uint8_t transfer_file_time[19+1];
    sprintf(transfer_file_time, "%04d-%02d-%02d %02d:%02d:%02d",
            (filbuf.date >> 9) + 1980,
            (filbuf.date >> 5) & 0x0f,
            (filbuf.date) & 0x1f,
            (filbuf.time >> 11),
            (filbuf.time >> 5) & 0x3f,
            (filbuf.time) & 0x1f);

    printf("--\n");
    printf("File Size: %d\n", transfer_file_size);
    printf("File Name: %s\n", transfer_file_name);
    printf("File Time: %s\n", transfer_file_time);
    printf("--\n");

    // eye catch and header
    if (write_rs232c("RSTX7650", 8, timeout) != 0) {
      printf("error: transfer error.\n");
      goto exit;
    }
    if (write_rs232c((uint8_t*)&transfer_file_size, 4, timeout) != 0) {
      printf("error: transfer error.\n");
      goto exit;
    }
    write_rs232c(transfer_file_name, 32, timeout);
    write_rs232c(transfer_file_time, 19, timeout);
    write_rs232c(".................", 17, timeout);

    // open file
    fp = fopen(input_file_name, "rb");
    if (fp == NULL) {
      printf("error: file open error.\n");
      goto exit;
    }

    // end of file flag
    int16_t eof = 0;

    // total sent size
    size_t total_size = 0;

    // initial crc
    uint32_t crc = 0;

    // start time
    uint32_t t0 = ONTIME();

    for (;;) {

      // check ESC key to exit
      if (B_KEYSNS() != 0) {
        int16_t scan_code = B_KEYINP() >> 8;
        if (scan_code == 0x01) {
          printf("\rCanceled.\x1b[0K\n");
          rc = 1;
          goto exit;
        }
      }

      // read data in chunk
      size_t read_len = 0;
      do {
        size_t len = fread(chunk_data + read_len, 1, chunk_size - read_len, fp);
        read_len += len;
        if (len == 0) {
          eof = 1;
          break;
        }
      } while (read_len < chunk_size);

      if (read_len > 0) {

        uint32_t chunk_len = read_len;
        uint32_t chunk_crc = crc32(crc, chunk_data, chunk_len);

        if (write_rs232c((uint8_t*)&chunk_len, 4, timeout) != 0) {
          printf("error: rs232c write error or timeout.\n");
          goto exit;
        }
        if (write_rs232c(chunk_data, chunk_len, timeout) != 0) {
          printf("error: rs232c write error or timeout.\n");
          goto exit;
        }
        if (write_rs232c((uint8_t*)&chunk_crc, 4, timeout) != 0) {
          printf("error: rs232c write error or timeout.\n");
          goto exit;
        }

        total_size += chunk_len;

        crc = chunk_crc;

        uint32_t t1 = ONTIME();

        printf("\rSent %d bytes in %4.2f sec. (CRC=%X)", total_size, (t1 - t0) / 100.0, crc);

      }

      if (eof) {
        uint32_t last_chunk_len = 0;
        write_rs232c((uint8_t*)&last_chunk_len, 4, timeout);
        printf("\nTransfer completed.\n");
        break;
      }
    }

    fclose(fp);
    fp = NULL;

  }

  write_rs232c("RSTXDONE", 8, timeout);

  printf("--\n");
  printf("Closed communication link.\n");

  rc = 0;

exit:

  // close input file handle
  if (fp != NULL) {
    fclose(fp);
    fp = NULL;
  }

  // free buffer
  if (chunk_data != NULL) {
    _doscall_mfree(chunk_data);
    chunk_data = NULL;
  }

  // flush key buffer
  while (B_KEYSNS() != 0) {
    B_KEYINP();
  }

  return rc;
}