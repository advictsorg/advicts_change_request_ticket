# -*- coding: utf-8 -*-
# Copyright 2024  Advicts LTD.
# Part of advicts. See LICENSE file for full copyright and licensing details.
from odoo import fields, api, models


class CrReason(models.TransientModel):
    _name = "cr.save.reason"
    _description = "CR Reason"

    name = fields.Text(string="Reason")
    reason_type = fields.Selection([
        ('work_hours', 'Outside Work Hours'),
        ('holiday', 'Weekend/Holiday'),
        ('short_notice', 'Short Notice'),
        ('operating_hour', 'Outside Operating Hours')
    ], string="Reason Type")

    def action_save(self):
        active_id = self._context.get('active_id')
        change_id = self.env['change.request'].browse(active_id)

        reason_field_mapping = {
            'work_hours': 'reason_work_hours',
            'holiday': 'reason_holiday',
            'short_notice': 'reason_short_notice',
            'operating_hour': 'reason_operating_hour'
        }

        field_to_update = reason_field_mapping.get(self.reason_type)
        if field_to_update:
            change_id.write({
                field_to_update: self.name
            })
