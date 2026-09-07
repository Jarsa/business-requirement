# Copyright 2017-2019 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import UserError
from odoo.tests import common


class BusinessRequirementTestBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # This is for reducing the diff coming from TransactionCase
        self = cls
        # Configure.
        self.BR = self.env["business.requirement"]
        self.br = self.BR.create({"description": "test"})


class BusinessRequirementTest(BusinessRequirementTestBase):
    def test_message_post(self):
        self.message = self.br.with_context(
            **{"default_model": "business.requirement", "default_res_id": self.br.id}
        ).message_post(
            body="Test Body",
            message_type="notification",
            subtype_id=self.env.ref("mail.mt_note").id,
            **{},
        )
        self.assertEqual(self.message.subject, f"Re: {self.br.name}-test")

    def test_br_name_search(self):
        br_vals = {"name": " test", "description": "test"}
        self.br.create(br_vals)
        self.assertTrue(self.br.name_search(name="test"))

    def test_create_name_sequence(self):
        name = self.env["ir.sequence"].next_by_code("business.requirement")
        br_vals = {"name": "/", "description": "test"}
        len_seq = name[2:]
        seq = "BR" + str(int(len_seq) + 1).zfill(int(len(len_seq)))
        res = self.BR.create(br_vals)
        self.assertEqual(seq, res.name)

    def test_br_read_group(self):
        state, count = self.env["business.requirement"]._read_group(
            [], ["state"], ["__count"]
        )[0]
        self.assertTrue(state)
        self.assertTrue(count)

    def test_get_portal_confirmation_action(self):
        self.portal_confirmation_action = self.br.get_portal_confirmation_action()
        self.assertEqual(self.portal_confirmation_action, "none")

    def test_compute_access_url(self):
        self.assertEqual(self.br.access_url, f"/my/business_requirement/{self.br.id}")

    def test_portal_publish_button(self):
        self.assertFalse(self.br.portal_published)

    def test_report(self):
        res = self.env["ir.actions.report"]._render_qweb_html(
            "business_requirement.br_report", self.br.ids
        )
        self.assertRegex(str(res[0]), self.br.name)


class BusinessRequirementCategoryTest(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Category = cls.env["business.requirement.category"]
        cls.parent = cls.Category.create({"name": "Purchase"})
        cls.child = cls.Category.create(
            {"name": "Goods Reception", "parent_id": cls.parent.id}
        )

    def test_complete_name(self):
        self.assertEqual(self.child.complete_name, "Purchase / Goods Reception")
        self.assertEqual(self.child.display_name, "Purchase / Goods Reception")

    def test_complete_name_recomputed_on_rename(self):
        self.parent.name = "Procurement"
        self.assertEqual(self.child.complete_name, "Procurement / Goods Reception")

    def test_child_ids(self):
        self.assertEqual(self.parent.child_ids, self.child)

    def test_child_of_search(self):
        found = self.Category.search([("id", "child_of", self.parent.id)])
        self.assertIn(self.child, found)

    def test_recursion_is_rejected(self):
        # _parent_store raises this on its own; no custom constraint needed.
        with self.assertRaises(UserError):
            self.parent.parent_id = self.child


class BusinessRequirementKanbanStateTest(common.TransactionCase):
    def test_kanban_state_uses_the_key_the_widget_paints(self):
        """`state_selection` only colours `blocked` red and `done` green."""
        selection = dict(
            self.env["business.requirement"]._fields["kanban_state"].selection
        )
        self.assertIn("blocked", selection)
        self.assertNotIn("on_hold", selection)

    def test_form_uses_a_widget_that_exists_in_19(self):
        arch = self.env.ref("business_requirement.view_business_requirement_form").arch
        self.assertIn('widget="state_selection"', arch)
        self.assertNotIn("kanban_state_selection", arch)
