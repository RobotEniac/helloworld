// =====================================================
//       Filename:  unlink.c
//         Author:  roboteniac <>
//        Created:  2017/06/07
//    Description:  
//    Copyright (c) 2017, roboteniac, All rights reserved. 
// =====================================================

#include <dirent.h>     /* Defines DT_* constants */
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <string.h>

#define handle_error(msg) \
    do { perror(msg); exit(EXIT_FAILURE); } while (0)

struct linux_dirent {
    long           d_ino;
    off_t          d_off;
    unsigned short d_reclen;
    char           d_name[];
};

#define BUF_SIZE 1024*1024*5

int main(int argc, char *argv[])
{
    int fd, nread;
    char buf[BUF_SIZE];
    struct linux_dirent *d;
    int bpos;
    char d_type;
    int idx;

    fd = open(argc > 1 ? argv[1] : ".", O_RDONLY | O_DIRECTORY);
    if (fd == -1)
        handle_error("open");

    idx = 0;
    for ( ; ; ) {
        nread = syscall(SYS_getdents, fd, buf, BUF_SIZE);
        if (nread == -1)
            handle_error("getdents");

        if (nread == 0)
            break;

        for (bpos = 0; bpos < nread;) {
            d = (struct linux_dirent *) (buf + bpos);
            d_type = *(buf + bpos + d->d_reclen - 1);
            if( d->d_ino != 0 && d_type == DT_REG ) {
                // printf("%s\n", (char *)d->d_name );
                if (strncmp(d->d_name, "BAAS_", 5) == 0) {
                    unlink(d->d_name);
                    if (++idx > 1000) {
                        printf("delete files\n");
                        idx = 0;
                    }
                }
            }
            bpos += d->d_reclen;
        }
    }

    exit(EXIT_SUCCESS);
}


