# Copyright 2026 Jarsa Sistemas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    """Rename the kanban state `on_hold` into `blocked`.

    Odoo's state widget only paints `blocked` red, so the value had to take the
    name every other kanban state uses. The label is unchanged.
    """
    cr.execute(
        """
        UPDATE business_requirement
        SET kanban_state = 'blocked'
        WHERE kanban_state = 'on_hold'
        """
    )
