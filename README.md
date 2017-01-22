# cuckoo-bird-encryption
New form of encryption using content on a selected web site to carry your message instead of sending an encrypted message.

# Components
* __The application__: a mobile application that complies with protocols defined here, that both the sender and receiver must run to exchange messages.
* __QR code__: to bootstrap the application, sender sends receiver a QR code containing a secret key used for all future communication between the two parties.  The sender uses a different QR code for each recipient
* __Selected URL__: each message requires that an URL be selected that carries the content of the message.  It is anticipated that the URL content not change so fast that the message cannot be retrieved.
* __Message__: a message will be obscured, not encrypted, by loading the content of the selected URL and using an algorithm to point to different parts of the content where the message can be found.
* __Pointer message__: what the sender sends to receiver.  It contains only pointers to different parts of the content.
* __Cuckoo bird__: some species are [obligate brood parasites](https://en.wikipedia.org/wiki/Cuckoo#Brood_parasitism) and lay their eggs in the nests of other birds.  This form of encryption works the same way in that it never transmits the message from sender to receiver, but "lays its eggs" in the content of the selected URL, and transmits pointers to parts of the content at the selected URL.  This is the **main benefit** of this encryption in that the pointer message can never be deciphered into the original message -- you need the content of the selected URL to obtain the message.  If the URL content changes, the message is lost forever, which is a **benefit** in that messages is short-lived and immune to future attacks.
* __ReadThenBurn__: a [web service](https://readthenburn.com/) used to initially introduce a sender and receiver.  Only when the receiver actually obtains the message will they know it was not intercepted.
* __Random content site__: a web site where you can grab an URL to random data that lives for a short duration (such as one minute), and the URL is forever invalid afterward

# Bootstrap
The application will generate an initial secret key K that the recipient will import into their application once, to be used on all future communications between both sender and recipient.  It will avoid detection by being passed to ReadThenBurn for a one-time-URL sent to the recipient to obtain the secret key K.  If intercepted this process continues until it is not intercepted.

When the message is ready to be sent, the sender selects an URL from anywhere on the Internet, possibly a random content site.  It must be stable enough to not change before the reciepient receives the message.

The content of the selected URL will be loaded.  Using a simple algorithm, each character of the original message will be found inside the content of the selected URL, and this pointer is appended to the pointer message.

The application will use the [TOTP algorithm](https://en.wikipedia.org/wiki/Time-based_One-time_Password_Algorithm) to generate a one-time password used to encrypt the selected URL.

The selected URL and pointer message is sent to the recipient.

The recipient loads the selected URL content, and reverses the process by turning each fragment of the pointer message into a character of the original message.  The selected URL is permanently discarded.  The original message is then displayed to the recipient.  The message is not stored inside the application so that the message is lost forever in a short amount of time.
