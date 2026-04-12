---
name: cheatsheet-linux-privesc
description: Linux privilege escalation checklist and techniques
---

# Linux Privilege Escalation Checklist

## Quick Wins
```bash
# Check sudo permissions
sudo -l

# Find SUID binaries
find / -perm -4000 -type f 2>/dev/null

# Check for writable /etc/passwd
ls -la /etc/passwd /etc/shadow

# Check cron jobs
cat /etc/crontab
ls -la /etc/cron.*
crontab -l

# Check for capabilities
getcap -r / 2>/dev/null
```

## System Enumeration
```bash
# OS and kernel
uname -a
cat /etc/os-release
cat /proc/version

# Users and groups
id
whoami
cat /etc/passwd | grep -v nologin
cat /etc/group

# Network
ip a
netstat -tulpn
ss -tulpn

# Running processes
ps aux
ps aux | grep root
```

## Exploitable SUID Binaries (GTFOBins)
Check https://gtfobins.github.io/ for exploitation:
- nmap, vim, find, bash, more, less, nano, cp, mv
- python, perl, ruby, lua, php
- env, awk, sed, tar, zip

## Writable Paths
```bash
# World-writable directories
find / -writable -type d 2>/dev/null

# Writable files owned by root
find / -writable -user root -type f 2>/dev/null

# Check PATH for writable directories
echo $PATH | tr ':' '\n' | xargs -I{} ls -ld {}
```

## Automated Tools
```bash
# LinPEAS
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh

# Linux Exploit Suggester
./linux-exploit-suggester.sh

# LinEnum
./LinEnum.sh
```

## Common Kernel Exploits
- DirtyPipe (CVE-2022-0847) - Linux 5.8+
- DirtyCow (CVE-2016-5195) - Linux 2.6.22-4.8
- PwnKit (CVE-2021-4034) - Polkit pkexec
- Baron Samedit (CVE-2021-3156) - sudo < 1.9.5p2

Use `searchsploit` to find exploits for the specific kernel version.
