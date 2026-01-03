#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>

int main() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    struct sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(1234);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    connect(sock, (struct sockaddr*)&addr, sizeof(addr));

    const char *cmd = "SET foo 42\n";
    send(sock, cmd, strlen(cmd), 0);

    char buf[1024];
    int n = recv(sock, buf, sizeof(buf)-1, 0);
    buf[n] = 0;
    printf("Server: %s\n", buf);

    close(sock);
}
