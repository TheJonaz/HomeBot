# HomeBot

**A lightweight IRC bot written 100% by Claude Code in Python.**

> Version 0.0.0.1 — by Jonaz &lt;irc@thern.io&gt;

---

## Features

- Connects to IRC over TCP or SSL
- Auto-reconnects on disconnect
- CTCP VERSION support
- Privileged commands restricted by `user@host` mask
- All commands via private message or NOTICE only

---

## Requirements

- Python 3.x
- No external dependencies

---

## Installation

```bash
git clone https://github.com/youruser/homebot.git
cd homebot
```

Edit `bot.conf` to match your network and preferences, then run:

```bash
python3 HomeBot.py
```

---

## Configuration

All settings live in `bot.conf`:

```ini
[irc]
server   = irc.efnet.org
port     = 6667
ssl      = false
nick     = HomeBot
realname = HomeBot IRC Bot
channel  = #Home

[bot]
master = *raven@*.thern.io
```

| Setting | Description |
|---------|-------------|
| `server` | IRC server hostname |
| `port` | IRC server port |
| `ssl` | Enable SSL (`true`/`false`) |
| `nick` | Bot's IRC nick |
| `realname` | Bot's real name field |
| `channel` | Channel to join on connect |
| `master` | `user@host` glob pattern for privileged commands |

---

## Commands

All commands must be sent via **private message or NOTICE**. Public channel commands are ignored.

| Command | Access | Description |
|---------|--------|-------------|
| `!HomeBot` | Anyone | Returns version and author info. |
| `!restart` | Master only | Restarts the bot as a new process. |
| `!die` | Master only | Sends QUIT and kills the bot process. |

---

## CTCP

| Request | Response |
|---------|----------|
| `VERSION` | `HomeBot 0.0.0.1 by Jonaz <irc@thern.io>` |

---

## Author

Jonaz &lt;irc@thern.io&gt;
