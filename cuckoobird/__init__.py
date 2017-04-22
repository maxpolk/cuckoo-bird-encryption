# This file is part of Cuckoo Bird Encryption, a secure messaging solution.
# Copyright (C) 2017  Max Polk <maxpolk@gmail.com>
# License located at http://www.gnu.org/licenses/gpl-3.0.html
'''
This is the main cuckoobird package of Cuckoo Bird Encryption.
'''

# EACH RELEASE MODIFY: __software_date__ and __software_type__

# Last two digits of year, followed by two digit month.
# YYMM of release date, restrict to [0-9]{4} (used by setup.py)
__software_date__ = "1704"

# Type of release, use "a" for alpha, "b" for beta, "c" for release candidate,
# and "" (the empty string) or "final" for final release version.
__software_type__ = "b"

# Name of this software
software_name = "Cuckoo Bird Encryption"

# Sofware version concatenates date and type (list of versions sort perfectly)
software_version = "{}.{}".format (__software_date__, __software_type__)

# Short description of this software
software_description = "a secure messaging solution"

# Long description of this software
software_long_description = '''
Cuckoo Bird Encryption is a secure messaging solution that employs a novel concept to use any web resource to store the plain text, rather than embedding it in an obscured form inside the message.  What is sent as the message is pointers to parts of the content of the web resource, so that without the selected URL, you cannot decipher the message.

The goal of Cuckoo Bird Encryption is to experiment with creating a secure messaging solution using something other than strong math on plain text.  Using a web resource to store your "eggs" and transmitting only pointers to it decentralizes the problem, and adds a dimension of complexity to any attack.  First, the plain text cannot be reconstituted using only the message, you need the contents of a web resource as well, eliminating brute force attacks.  Second, the web resource is ephemeral, likely to change over time, which spares you from future attacks using stronger algorithms or computing hardware.  Third, if the selected URL is to site whose content can only be obtained once before it self-destructs, then a third party having full access to message doesn't help.

RandomContentSite provides a web site that hands out resources containing random data.  Each resource self-destructs upon reading, giving attackers of solutions like Cuckoo Bird Encryption difficulty trying to abuse the protocol.

Ephemeral web resources play a role in protocols like self-destructing messages.  Cuckoo Bird Encryption uses random content web resources to store the message, that is, the message consists of pointers to the random content.  If the random content disappears after first use, the message cannot be deciphered by anyone else later.

This project is licensed under version 3 of the GNU General Public License, which you can read here: http://www.gnu.org/licenses/gpl-3.0.html
'''

# License
software_license = '''
This file is part of Cuckoo Bird Encryption, a secure messaging solution.
Copyright (C) 2017  Max Polk <maxpolk@gmail.com>
License located at http://www.gnu.org/licenses/gpl-3.0.html

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

software_short_license = '''
Copyright (C) 2017  Max Polk <maxpolk@gmail.com>
License located at http://www.gnu.org/licenses/gpl-3.0.html
'''

software_abbreviation_license = "GNU GPL"
