/* OpenERP, Open Source Management Solution
 * Copyright (C) 2014  Grupo ESOC <www.grupoesoc.es>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

openerp.mail_full_expand = function (instance) {
    instance.mail.ThreadMessage.include({
        bind_events: function () {
            this._super.apply(this, arguments);
            this.$('.oe_full_expand').on('click', this.on_message_full_expand);
        },

        on_message_full_expand: function() {
            // Get the action data and execute it to open the full view
            var do_action = this.do_action,
                msg_id = this.id;

            this.rpc("/web/action/load", {
                "action_id": "mail_full_expand.act_window",
            })
            .done(function(action) {
                action.res_id = msg_id;
                do_action(action);
            });
        }
    });
};
