import datetime
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    cr_hours = fields.Float(string='Change Request Hours')
    start_time = fields.Float(string="Request Start Time")
    end_time = fields.Float(string="Request End Time")

    create_start_time = fields.Float(string="Create Start Time")
    create_end_time = fields.Float(string="Create End Time")

    @api.constrains('start_time', 'end_time')
    def _check_time_range(self):
        for record in self:
            if not 0 <= record.start_time <= 24:
                raise ValidationError(_("Start time must be between 0 and 24."))
            if not 0 <= record.end_time <= 24:
                raise ValidationError(_("End time must be between 0 and 24."))

    @api.constrains('create_start_time', 'create_end_time')
    def _check_time_range(self):
        for record in self:
            if not 0 <= record.create_start_time <= 24:
                raise ValidationError(_("Start time must be between 0 and 24."))
            if not 0 <= record.create_end_time <= 24:
                raise ValidationError(_("End time must be between 0 and 24."))


class CrSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    cr_hours = fields.Float(string='Change Request Hours', default=lambda self: self.env.company.cr_hours)
    start_time = fields.Float(string="Request Start Time", default=lambda self: self.env.company.start_time)
    end_time = fields.Float(string="Request End Time", default=lambda self: self.env.company.end_time)
    create_start_time = fields.Float(string="Create Start Time",
                                     default=lambda self: self.env.company.create_start_time)
    create_end_time = fields.Float(string="Create End Time", default=lambda self: self.env.company.create_end_time)

    @api.constrains('start_time', 'end_time')
    def _check_time_range(self):
        for record in self:
            if not 0 <= record.start_time <= 24:
                raise ValidationError(_("Start time must be between 0 and 24."))
            if not 0 <= record.end_time <= 24:
                raise ValidationError(_("End time must be between 0 and 24."))

    @api.constrains('create_start_time', 'create_end_time')
    def _check_time_range(self):
        for record in self:
            if not 0 <= record.create_start_time <= 24:
                raise ValidationError(_("Start time must be between 0 and 24."))
            if not 0 <= record.create_end_time <= 24:
                raise ValidationError(_("End time must be between 0 and 24."))

    def set_values(self):
        super(CrSetting, self).set_values()
        self.env.company.cr_hours = self.cr_hours
        self.env.company.start_time = self.start_time
        self.env.company.end_time = self.end_time
        self.env.company.create_start_time = self.create_start_time
        self.env.company.create_end_time = self.create_end_time

    @api.model
    def get_values(self):
        res = super(CrSetting, self).get_values()
        res.update(
            cr_hours=self.env.company.cr_hours,
            start_time=self.env.company.start_time,
            end_time=self.env.company.end_time,
            create_start_time=self.env.company.create_start_time,
            create_end_time=self.env.company.create_end_time,
        )
        return res
