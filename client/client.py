import socket
import struct
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    '--ip_addr', help='ip address of the redis cache server', type=str, default="127.0.0.1")
parser.add_argument(
    '--port', help='port configured for redis cache server', type=int, default=1234)

args = parser.parse_args()
server_ip_addr = args.ip_addr
server_port = args.port

# ---------- low-level helpers ----------

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise RuntimeError("socket closed early")
        data += chunk
    return data


def send_cmd(sock, args):
    """
    args: list of strings, e.g. ["set", "a", "100"]
    """
    body = struct.pack("<I", len(args))   # argc
    for a in args:
        b = a.encode()
        body += struct.pack("<I", len(b)) + b

    # prepend total length
    sock.sendall(struct.pack("<I", len(body)) + body)

    # read response
    resp_len = struct.unpack("<I", recv_exact(sock, 4))[0]
    return recv_exact(sock, resp_len)


# ---------- response decoding ----------

TAG_NIL = 0
TAG_ERR = 1
TAG_STR = 2
TAG_INT = 3
TAG_DBL = 4
TAG_ARR = 5


def parse_resp(buf, indent=0):
    pad = " " * indent
    tag = buf[0]
    data = buf[1:]

    if tag == TAG_NIL:
        print(pad + "NIL")

    elif tag == TAG_STR:
        strlen = struct.unpack("<I", data[:4])[0]
        s = data[4:4+strlen].decode()
        print(pad + f"STR: {s}")

    elif tag == TAG_INT:
        val = struct.unpack("<q", data[:8])[0]
        print(pad + f"INT: {val}")

    elif tag == TAG_DBL:
        val = struct.unpack("<d", data[:8])[0]
        print(pad + f"DBL: {val}")

    elif tag == TAG_ERR:
        code = struct.unpack("<I", data[:4])[0]
        strlen = struct.unpack("<I", data[4:8])[0]
        msg = data[8:8+strlen].decode()
        print(pad + f"ERR {code}: {msg}")

    elif tag == TAG_ARR:
        n = struct.unpack("<I", data[:4])[0]
        print(pad + f"ARR ({n} elements)")
        off = 4
        for i in range(n):
            sub_tag = data[off]
            off += 1

            if sub_tag == TAG_STR:
                l = struct.unpack("<I", data[off:off+4])[0]
                off += 4
                s = data[off:off+l].decode()
                off += l
                print(pad + "  STR:", s)

            elif sub_tag == TAG_DBL:
                v = struct.unpack("<d", data[off:off+8])[0]
                off += 8
                print(pad + "  DBL:", v)

            elif sub_tag == TAG_INT:
                v = struct.unpack("<q", data[off:off+8])[0]
                off += 8
                print(pad + "  INT:", v)

            else:
                print(pad + "  UNKNOWN SUBTAG:", sub_tag)
                break
    else:
        print(pad + "UNKNOWN TAG:", tag)


# ---------- main ----------

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip_addr, server_port))  # change IP if needed

    print("SET a 100")
    parse_resp(send_cmd(s, ["set", "a", "100"]))

    print("\nGET a")
    parse_resp(send_cmd(s, ["get", "a"]))

    print("\nPTTL a")
    parse_resp(send_cmd(s, ["pttl", "a"]))

    print("\nPEXPIRE a 3000")
    parse_resp(send_cmd(s, ["pexpire", "a", "3000"]))

    print("\nKEYS")
    parse_resp(send_cmd(s, ["keys"]))

    print("\nZADD zs 1.5 foo")
    parse_resp(send_cmd(s, ["zadd", "zs", "1.5", "foo"]))

    print("\nZSCORE zs foo")
    parse_resp(send_cmd(s, ["zscore", "zs", "foo"]))

    print("\nZQUERY zs 0 '' 0 10")
    parse_resp(send_cmd(s, ["zquery", "zs", "0", "", "0", "10"]))

    time.sleep(1)
    s.close()


if __name__ == "__main__":
    main()

