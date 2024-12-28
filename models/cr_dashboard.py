# -*- coding: utf-8 -*-
# Copyright 2024  Advicts LTD.
# Part of advicts. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class CrDashboard(models.Model):
    _name = 'cr.dashboard'
    _description = "Change Request Dashboard"

    name = fields.Char(string="Dashboard")

    @api.model
    def get_cr_stats(self):
        today_date = fields.Date.today()
        cr_obj = self.env['change.request'].sudo()
        active_cr = cr_obj.search_count([('stage', '=', 'bid_submission')])
        cr_in_process = cr_obj.search_count([('stage', 'in', ['bid_evaluation', 'bid_selection'])])

        data = {
            'total_cr': cr_obj.search_count([]),
            'active_cr': active_cr,
            'cr_in_process': cr_in_process,
            'cr_time_line': self.cr_time_line(),
        }
        return data

    def cr_time_line(self):
        cr = []
        cr_data = self.env['change.request'].search([])
        for t in cr_data:
            if t.stage not in ['draft', 'cancel', 'done']:
                cr.append({
                    'name': str(t.name),
                    'start_date': str(t.start_date),
                    'end_date': str(t.end_date),
                })
        return cr
