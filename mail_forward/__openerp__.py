# -*- encoding: utf-8 -*-

# OpenERP, Open Source Management Solution
# Copyright (C) 2014  Grupo ESOC <www.grupoesoc.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

{
    "name": "Message Forward",
    "version": "2.3.0",
    "category": "Social Network",
    "author": "Grupo ESOC",
    "license": "AGPL-3",
    "website": "http://www.grupoesoc.es",
    "installable": True,
    "application": False,
    "summary": "Add option to forward messages",
    "description": """
Messages can be forwarded in two ways:

- **To another object of the database:**

  - All its followers are notified according to their settings.

  - If the message contains attachments and the user marks the *Move
    attachments* option, those get attached to the new object.

- **To other contacts:**

  - They recieve the forwarded message according to the usual notification
    rules of OpenERP.

*Technical note: Internally, forwarded messages are copies of original ones,
but attachments are exactly the originals to avoid duplicating disk space.
Keep that in mind when managing permissions.*
""",
    "depends": [
        "mail",
        "web",
    ],
    "data": [
        "wizard/mail_forward.xml",
    ],
    'css': [
        'static/src/css/mail_forward.css',
    ],
    'js': [
        'static/src/js/mail_forward.js',
    ],
    'qweb': [
        'static/src/xml/mail_forward.xml',
    ],
}
