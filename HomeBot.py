import ssl
import socket
import time
import threading
import os
import sys
import fnmatch
import subprocess
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "bot.conf"))

SERVER = config["irc"]["server"]
PORT = config.getint("irc", "port")
SSL = config.getboolean("irc", "ssl")
NICK = config["irc"]["nick"]
REALNAME = config["irc"]["realname"]
CHANNEL = config["irc"]["channel"]
MASTER = config["bot"]["master"]

VERSION = "0.0.0.1"

irc_sock = None
irc_lock = threading.Lock()
irc_ready = threading.Event()


def send(sock, msg):
    print(f">> {msg}")
    sock.send((msg + "\r\n").encode("utf-8"))


def send_to_channel(msg):
    irc_ready.wait(timeout=30)
    with irc_lock:
        if irc_sock:
            try:
                send(irc_sock, f"PRIVMSG {CHANNEL} :{msg}")
            except Exception as e:
                print(f"Failed to send to channel: {e}")


def connect():
    global irc_sock
    ctx = ssl.create_default_context() if SSL else None
    while True:
        try:
            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = ctx.wrap_socket(raw_sock, server_hostname=SERVER) if ctx else raw_sock
            sock.connect((SERVER, PORT))
            with irc_lock:
                irc_sock = sock

            send(sock, f"NICK {NICK}")
            send(sock, f"USER {NICK} 0 * :{REALNAME}")

            buf = ""
            joined = False

            while True:
                data = sock.recv(2048).decode("utf-8", errors="replace")
                if not data:
                    break
                buf += data
                lines = buf.split("\r\n")
                buf = lines.pop()

                for line in lines:
                    print(f"<< {line}")

                    if line.startswith("PING"):
                        send(sock, line.replace("PING", "PONG"))

                    parts = line.split()

                    if not joined and len(parts) >= 2 and parts[1] in ("376", "422", "001"):
                        time.sleep(1)
                        send(sock, f"JOIN {CHANNEL}")
                        joined = True
                        irc_ready.set()

                    if len(parts) >= 4 and parts[1] in ("PRIVMSG", "NOTICE"):
                        target = parts[2]
                        msg_body = " ".join(parts[3:])[1:]
                        nick_from = parts[0].split("!")[0].lstrip(":")
                        print(f"[{target}] <{nick_from}> {msg_body}")

                        is_private = not target.startswith("#") and not target.startswith("&")

                        if msg_body == "\x01VERSION\x01":
                            send(sock, f"NOTICE {nick_from} :\x01VERSION HomeBot {VERSION} by Jonaz <irc@thern.io>\x01")

                        if is_private and msg_body.strip() in ("!restart", "!die"):
                            userhost = parts[0].lstrip(":").split("!")[1] if "!" in parts[0] else ""
                            if fnmatch.fnmatch(userhost, MASTER):
                                if msg_body.strip() == "!restart":
                                    send(sock, f"PRIVMSG {nick_from} :Restarting...")
                                    time.sleep(1)
                                    subprocess.Popen([sys.executable] + sys.argv)
                                else:
                                    send(sock, f"QUIT :Bye!")
                                    time.sleep(1)
                                os._exit(0)

        except Exception as e:
            print(f"IRC error: {e}")
        finally:
            irc_ready.clear()
            with irc_lock:
                irc_sock = None

        print("Disconnected. Reconnecting in 30s...")
        time.sleep(30)


if __name__ == "__main__":
    print(f"Connecting to {SERVER}:{PORT} as {NICK}...")
    connect()
