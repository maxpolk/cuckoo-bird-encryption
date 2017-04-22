# cuckoo-bird-encryption
New form of encryption using content on a selected web site to carry your message instead of sending an encrypted message.

## Components
* __The application__: a mobile application that complies with protocols defined here, that both the sender and receiver must run to exchange messages.
* __Selected URL__: each message requires that an URL be selected that carries the content of the message.  It is anticipated that the URL content not change so fast that the message cannot be retrieved.  The type of content is irrelevant since it is used as data, so it can be an image, html, octet stream, or anything else.
* __Message__: a message will be obscured, not encrypted, by loading the content of the selected URL and using an algorithm to point to different parts of the content where the message can be found.
* __Pointer message__: what the sender sends to receiver.  It contains only pointers to different parts of the content.
* __Cuckoo bird__: some species are [obligate brood parasites](https://en.wikipedia.org/wiki/Cuckoo#Brood_parasitism) and lay their eggs in the nests of other birds.  This form of encryption works the same way in that it never transmits the message from sender to receiver, but "lays its eggs" in the content of the selected URL, and transmits pointers to parts of the content at the selected URL.  This is the **main benefit** of this encryption in that the pointer message can never be deciphered into the original message -- you need the content of the selected URL to obtain the message.  If the URL content changes, the message is lost forever, which is a **benefit** in that messages is short-lived and immune to future attacks.
* __ReadThenBurn__: a [web service](https://readthenburn.com/) used to initially introduce a sender and receiver.  Only when the receiver actually obtains the message will they know it was not intercepted.
* __Random content site__: a web site where you can grab an URL to random data that lives for a short duration (such as one minute), and the URL is forever invalid afterward. An option is to use this as your selected URL.

## Sending messages
The application will generate an initial secret key K that the recipient will import into their application once, to be used on all future communications between both sender and recipient.  It will avoid detection by being passed to ReadThenBurn for a one-time-URL sent to the recipient to obtain the secret key K.  If intercepted this process continues until it is not intercepted.

When the message is ready to be sent, the sender selects an URL from anywhere on the Internet, possibly a random content site.  It must be stable enough to not change before the reciepient receives the message.

The content of the selected URL will be loaded.  Using a simple algorithm, each character of the original message will be found inside the content of the selected URL, and this pointer is appended to the pointer message.  The sender has the option to discard the message so that a compromised device cannot reconstitute the message.

The application will use the [TOTP algorithm](https://en.wikipedia.org/wiki/Time-based_One-time_Password_Algorithm) to generate a one-time password used to encrypt the selected URL.

The selected URL and pointer message is sent to the recipient via the application.

The recipient application loads the selected URL content, and deciphers the pointer message by turning each fragment of the pointer message into a character of the original message.  The selected URL is permanently discarded.  The original message is then displayed to the recipient.  The recipient has the option to not store the original message inside the application so that the message is lost forever in a short amount of time, and a compromised device cannot reconstitute the message.

If both sender and recipient elect to discard the original message, then it is impossible for a compromised device on either side to reveal the message.

## Projects
The randomcontentsite package contains a web site that generates random data and
stores it as a temporary URL.

## Installing
To install a Python script to run as a system service, you have several options.  Let us
take RandomContentSite.py as an example service.

### Ubuntu under systemd
To install on Ubuntu under systemd, create a service file:

File location:

    /etc/systemd/system/python3-randomdata.service

File contents:

    [Unit]
    Description=Python3 randomdata site
    After=network.target
    
    [Service]
    Type=simple
    WorkingDirectory=/var/www/python/cuckoo-bird-encryption
    Environment="PYTHONPATH=/var/www/python/cuckoo-bird-encryption"
    ExecStart=/usr/bin/python3 -u cuckoobird/RandomContentSite.py random 8010
    StandardOutput=journal
    StandardError=journal
    
    [Install]
    WantedBy=multi-user.target

Enable:

    systemctl daemon-reload
    systemctl enable python3-randomdata

Start and stop:

    systemctl start test-server
    systemctl stop test-server

View log (we ran python3 -u for unbuffered output so it shows immediately in log):

    journalctl [-f] -u python3-random

### Cygwin Windows service under cygrunsrv
To install as a Cygwin Windows service, use cygrunsrv as follows.
Perform the following as administrator.

Install (no userspace drives mapped, use something like /cygdrive/c to find script):

    cygrunsrv --install testserver
              --path /usr/bin/python3
              --args "/cygdrive/c/WHATEVER/RandomContentSite.py"
              --termsig INT                 # service stop signal (graceful shutdown)
              --shutsig TERM                # system shutdown signal (fast shutdown)
              --shutdown                    # stop service at system shutdown

Start:

    cygrunsrv -S testserver

Stop:

    cygrunsrv -E testserver

Uninstall:

    cygrunsrv -R testserver

### Native Python service under nssm
To install as a native Python Windows service, use nssm as follows.

Download nssm at http://nssm.cc/ and unzip, you'll use the correct nssm.exe
program for your OS (32-bit or 64-bit).

    Path:              C:\Apps\Python3\python.exe
    Startup directory: C:\WHATEVER
    Arguments:         RandomContentSite.py

### Run directly
To run directly, such as during local development:

    python3 RandomContentSite.py random 8010
