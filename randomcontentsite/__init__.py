# This file is part of Cuckoo Bird Encryption, a secure messaging solution.
# Copyright (C) 2017  Max Polk <maxpolk@gmail.com>
# License located at http://www.gnu.org/licenses/gpl-3.0.html
'''
This is the random content site subpackage of Cuckoo Bird Encryption.
'''

# EACH RELEASE MODIFY: __software_date__ and __software_type__

# Last two digits of year, followed by two digit month.
# YYMM of release date, restrict to [0-9]{4} (used by setup.py)
__software_date__ = "1701"

# Type of release, use "a" for alpha, "b" for beta, "c" for release candidate,
# and "" (the empty string) or "final" for final release version.
__software_type__ = "a"

# Name of this software
software_name = "Random content site"

# Sofware version concatenates date and type (list of versions sort perfectly)
software_version = "{}.{}".format (__software_date__, __software_type__)

# Short description of this software
software_description = "a web site that provides random content"

# Long description of this software
software_long_description = '''
This subpackage of Cuckoo Bird Encryption provides a web site that hands out resources containing random data.  Each resource self-destructs upon reading, giving attackers of solutions like Cuckoo Bird Encryption difficulty trying to abuse the protocol.

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
