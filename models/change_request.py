# -*- coding: utf-8 -*-
# Copyright 2024  Advicts LTD.
# Part of advicts. See LICENSE file for full copyright and licensing details.
from datetime import timedelta

from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError


class ChangeRequestTicket(models.Model):
    _name = 'change.request'
    _description = "Change Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", tracking=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    subject = fields.Char(string="Request Name", required=True, tracking=True, translate=True)
    start_date = fields.Datetime(string="Request Start Date", tracking=True)
    end_date = fields.Datetime(string="Request End Date", tracking=True)
    responsible_id = fields.Many2one('res.users',
                                     default=lambda self: self.env.user and self.env.user.id or False,
                                     string="Responsible")
    partner_id = fields.Many2many('res.partner', 'partner_change_request_rel', 'Customers')

    def open_reason_wizard(self, reason_type):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enter Reason',
            'res_model': 'cr.save.reason',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_reason_type': reason_type,
                'active_id': self.id
            }
        }

    def _check_is_reason_need(self):
        for record in self:
            record.is_need_reason = False
            for record in self:
                if record.start_date and record.end_date and record.create_date:
                    create_start_time = timedelta(hours=int(self.env.company.create_start_time - 3),
                                                  minutes=int((self.env.company.create_start_time % 1) * 60))
                    create_end_time = timedelta(hours=int(self.env.company.create_end_time - 3),
                                                minutes=int((self.env.company.create_end_time % 1) * 60))
                    create_date = timedelta(hours=record.create_date.hour, minutes=record.create_date.minute)
                    cr_hours = self.env.company.cr_hours
                    time_difference = record.start_date - record.create_date
                    start_time = timedelta(hours=int(self.env.company.start_time - 3),
                                           minutes=int((self.env.company.start_time % 1) * 60))
                    end_time = timedelta(hours=int(self.env.company.end_time - 3),
                                         minutes=int((self.env.company.end_time % 1) * 60))
                    start_date_time = timedelta(hours=record.start_date.hour, minutes=record.start_date.minute)
                    end_date_time = timedelta(hours=record.end_date.hour, minutes=record.end_date.minute)
                    create_weekday = record.create_date.weekday()

                    if time_difference < timedelta(hours=cr_hours) and not self.reason_short_notice:
                        record.is_need_reason = True
                    if (
                            create_date < create_start_time or create_date > create_end_time) and not record.reason_work_hours:
                        record.is_need_reason = True
                    if create_weekday in (4, 5) and not record.reason_holiday:
                        record.is_need_reason = True
                    if (start_date_time < start_time or end_date_time > end_time) and not record.reason_operating_hour:
                        record.is_need_reason = True

    def _date_validation(self):
        for record in self:
            if record.start_date and record.end_date and record.create_date:
                create_start_time = timedelta(hours=int(self.env.company.create_start_time - 3),
                                              minutes=int((self.env.company.create_start_time % 1) * 60))
                create_end_time = timedelta(hours=int(self.env.company.create_end_time - 3),
                                            minutes=int((self.env.company.create_end_time % 1) * 60))
                create_date = timedelta(hours=record.create_date.hour, minutes=record.create_date.minute)
                cr_hours = self.env.company.cr_hours
                time_difference = record.start_date - record.create_date
                start_time = timedelta(hours=int(self.env.company.start_time - 3),
                                       minutes=int((self.env.company.start_time % 1) * 60))
                end_time = timedelta(hours=int(self.env.company.end_time - 3),
                                     minutes=int((self.env.company.end_time % 1) * 60))
                start_date_time = timedelta(hours=record.start_date.hour, minutes=record.start_date.minute)
                end_date_time = timedelta(hours=record.end_date.hour, minutes=record.end_date.minute)
                create_weekday = record.create_date.weekday()

                if time_difference < timedelta(hours=cr_hours) and not self.reason_short_notice:
                    record.open_reason_wizard('short_notice')
                if (create_date < create_start_time or create_date > create_end_time) and not record.reason_work_hours:
                    record.open_reason_wizard('work_hours')
                if create_weekday in (4, 5) and not record.reason_holiday:
                    record.open_reason_wizard('holiday')
                if (start_date_time < start_time or end_date_time > end_time) and not record.reason_operating_hour:
                    record.open_reason_wizard('operating_hour')

    cr_impact_lines = fields.One2many('cr.impact.line', 'change_id', string="Impact list", tracking=True)
    cr_evaluation_lines = fields.One2many('cr.evaluation.line', 'change_id', string="Evaluation", tracking=True)

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    # -------------
    severity = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High'),
    ], default='0')
    summary_desc = fields.Text('Summary Description')
    details = fields.Text('Details')
    reason_holiday = fields.Char('Reason For Sent During Weekend')
    reason_work_hours = fields.Char('Reason For Sent Out of Selected Hours')
    reason_short_notice = fields.Char(string="Reason For Short Note", tracking=True)
    reason_operating_hour = fields.Char(string="Reason For Operating in Peak Hours", tracking=True)
    reject_reason = fields.Text('Reject Reason', tracking=True)
    reschedule_reason = fields.Text('Reschedule Reason', tracking=True)
    service_impact = fields.Boolean('Service Impact')
    service_impact_details = fields.Char('Service Impact Details')
    need_access = fields.Boolean('Need Access')
    access_permission_granted = fields.Boolean('Access Permission Granted')
    access_details = fields.Char('Access Details')
    user_ids = fields.Many2many('res.users', 'change_request_user_rel', 'change_request_id', 'user_id',
                                string="Involved parties")
    team_ids = fields.Many2many('sh.helpdesk.team', 'change_request_team_rel', 'change_request_id', 'team_id',
                                string="Related Teams", tracking=True)
    ticket_count = fields.Integer(string="ticket Count", compute="_compute_ticket_count")
    ticket_ids = fields.One2many('sh.helpdesk.ticket', 'change_id', 'Tickets')

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
        for record in self:
            record.ticket_count = len(record.ticket_ids)

    def action_view_tickets(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tickets',
            'view_mode': 'tree,form',
            'res_model': 'sh.helpdesk.ticket',
            'domain': [('change_id', '=', self.id)],
            'context': {
                'default_change_id': self.id,  # Default value for a field
                # 'default_partner_id': self.partner_id.ids,
            },
        }

    classification = fields.Many2one('cr.classification', string="Classification")
    # -------------
    desc = fields.Html(string="Description", tracking=True)
    stage = fields.Selection([('draft', 'New'),
                              ('waiting_t3_approval', 'Waiting T3 Approval'),
                              ('waiting_technical_approval', 'Waiting Technical Approval'),
                              ('submit_noc', 'Submit Ticket to NOC'),
                              ('impact_analyzing', 'Impact Analyzing'),
                              ('noc_decision', 'NOC Decision'),
                              ('reschedule', 'Reschedule'),
                              ('customer_impact', 'Customer Impact'),
                              ('customer_confirmation', 'Customer Confirmation'),
                              ('access_status', 'Access_status'),
                              ('operation_process', 'Operation Process'),
                              ('service_recovery', 'Service Recovery'),
                              ('involved_parties_recovery', 'Involved parties recovery'),
                              ('review', 'Review'),
                              ('done', 'Done'),
                              ('cancel', 'Canceled'),
                              ('reject', 'Rejected'),
                              ],
                             tracking=True,
                             copy=False,
                             default='draft')
    is_need_reason = fields.Boolean(compute='_check_is_reason_need')

    def submit(self):
        for rec in self:
            if rec.is_need_reason:
                if rec.start_date and rec.end_date and rec.create_date:
                    create_start_time = timedelta(hours=int(self.env.company.create_start_time - 3),
                                                  minutes=int((self.env.company.create_start_time % 1) * 60))
                    create_end_time = timedelta(hours=int(self.env.company.create_end_time - 3),
                                                minutes=int((self.env.company.create_end_time % 1) * 60))
                    create_date = timedelta(hours=rec.create_date.hour, minutes=rec.create_date.minute)
                    cr_hours = self.env.company.cr_hours
                    time_difference = rec.start_date - rec.create_date
                    start_time = timedelta(hours=int(self.env.company.start_time - 3),
                                           minutes=int((self.env.company.start_time % 1) * 60))
                    end_time = timedelta(hours=int(self.env.company.end_time - 3),
                                         minutes=int((self.env.company.end_time % 1) * 60))
                    start_date_time = timedelta(hours=rec.start_date.hour, minutes=rec.start_date.minute)
                    end_date_time = timedelta(hours=rec.end_date.hour, minutes=rec.end_date.minute)
                    create_weekday = rec.create_date.weekday()

                    if time_difference < timedelta(hours=cr_hours) and not self.reason_short_notice:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Enter Reason',
                            'res_model': 'cr.save.reason',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {
                                'default_reason_type': 'short_notice',
                                'active_id': rec.id
                            }
                        }
                    if (
                            create_date < create_start_time or create_date > create_end_time) and not rec.reason_work_hours:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Enter Reason',
                            'res_model': 'cr.save.reason',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {
                                'default_reason_type': 'work_hours',
                                'active_id': rec.id
                            }
                        }
                    if create_weekday in (4, 5) and not rec.reason_holiday:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Enter Reason',
                            'res_model': 'cr.save.reason',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {
                                'default_reason_type': 'holiday',
                                'active_id': rec.id
                            }
                        }
                    if (start_date_time < start_time or end_date_time > end_time) and not rec.reason_operating_hour:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': 'Enter Reason',
                            'res_model': 'cr.save.reason',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': {
                                'default_reason_type': 'operating_hour',
                                'active_id': rec.id
                            }
                        }
            else:
                group = self.env.ref('advicts_change_request_ticket.cr_t3_approval_group', raise_if_not_found=False)
                if group:
                    self._create_approval_activity(group, False, 'Approval Required', 'Need Manager Approval')
                rec.stage = 'waiting_t3_approval'

    def approve_t3(self):
        for rec in self:
            group = self.env.ref('advicts_change_request_ticket.cr_technical_approval_group', raise_if_not_found=False)
            if group:
                self._create_approval_activity(group, False, 'Approval Required', 'Need Manager Approval')
            rec.stage = 'waiting_technical_approval'

    def approve_technical(self):
        for rec in self:
            if rec.team_ids:
                for team in rec.team_ids:
                    if team.team_head:
                        self._create_approval_activity(not_user_id=team.team_head, title='Process Required',
                                                       message='Need Process')
            group = self.env.ref('advicts_change_request_ticket.cr_noc_group', raise_if_not_found=False)
            if group:
                self._create_approval_activity(group, False, 'Process Required', 'Need Process')
            rec.stage = 'submit_noc'

    def impact_analyzing(self):
        for rec in self:
            rec.stage = 'impact_analyzing'

    # in reschedule also
    def send_to_noc_decision(self):
        for rec in self:
            group = self.env.ref('advicts_change_request_ticket.cr_noc_group', raise_if_not_found=False)
            if group:
                self._create_approval_activity(group, False, 'Process Required', 'Need Process')
            rec.stage = 'noc_decision'

    def no_impact_analyzing(self):
        self.send_to_noc_decision()

    def reject_with_reason(self):
        for rec in self:
            self._create_approval_activity(False, rec.create_uid, 'Update Status Notification',
                                           'CR Update Status Notification')
            rec.stage = 'draft'

    def reschedule_with_reason(self):
        for rec in self:
            self._create_approval_activity(False, rec.create_uid, 'Update Status Notification',
                                           'CR Update Status Notification')
            rec.stage = 'reschedule'

    def noc_approve(self):
        for rec in self:
            self._create_approval_activity(False, rec.create_uid, 'Update Status Notification',
                                           'CR Update Status Notification')
            rec.stage = 'customer_impact'

    is_customer_notify = fields.Boolean()

    def customerNotification(self):
        for rec in self:
            mail_template = self.env.ref('advicts_change_request_ticket.custom_impact_mail_template')
            company_email = self.env.company.email
            if mail_template:
                mail_template.email_from = company_email
                for partner in rec.partner_id:
                    mail_template.email_to = partner.email
                    mail_template.send_mail(self.id, force_send=True)
                rec.is_customer_notify = True

    def customer_impact(self):
        for rec in self:
            rec.customer_impact_status = 'yes'
            rec.customerNotification()
            rec.stage = 'access_status'

    def no_customer_impact(self):
        for rec in self:
            rec.customer_impact_status = 'no'
            rec.stage = 'access_status'

    def customer_confirm(self):
        for rec in self:
            rec.customer_confirmation_status = 'yes'
            rec.stage = 'access_status'

    def customer_reject(self):
        for rec in self:
            rec.customer_confirmation_status = 'no'
            rec.stage = 'reschedule'

    def access_required(self):
        for rec in self:
            if rec.need_access:
                if rec.access_permission_granted:
                    rec.stage = 'operation_process'
                else:
                    rec.stage = 'reschedule'
            else:
                rec.stage = 'operation_process'

    def reschedule_by_operation(self):
        for rec in self:
            rec.stage = 'reschedule'

    def complete_by_operation(self):
        for rec in self:
            rec.stage = 'service_recovery'

    def confirm_service_recovery(self):
        for rec in self:
            if rec.user_ids:
                for user in rec.user_ids:
                    self.activity_schedule(
                        'mail.mail_activity_data_todo',
                        note=f'Update Status Notification',
                        user_id=user.id,
                        summary=_(f'Update Status Notification')
                    )
            rec.stage = 'involved_parties_recovery'

    def approve_involved_parties_recovery(self):
        for rec in self:
            rec.stage = 'review'

    def done(self):
        for rec in self:
            rec.stage = 'done'

    work_location = fields.Selection([('remote', 'Remote'),
                                      ('onsite', 'On-Site')],
                                     tracking=True,
                                     default='onsite')

    customer_impact_status = fields.Selection([('yes', 'Remote'),
                                               ('no', 'Cancel')],
                                              tracking=True,
                                              )

    customer_confirmation_status = fields.Selection([('yes', 'Remote'),
                                                     ('no', 'Cancel')],
                                                    tracking=True,
                                                    )

    # cancellation_reason = fields.Html(string="Cancellation Reason")
    # Address
    is_site_specific = fields.Boolean('Is Site Specific', compute='_compute_is_site_specific', store=True)

    @api.depends('work_location')
    def _compute_is_site_specific(self):
        for record in self:
            record.is_site_specific = True if record.work_location == 'onsite' else False

    zip = fields.Char(string='Pin Code', translate=True)
    street = fields.Char(string='Street1', translate=True)
    street2 = fields.Char(string='Street2', translate=True)
    city = fields.Char(string='City', translate=True)
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one("res.country.state",
                               string='State', readonly=False, store=True,
                               domain="[('country_id', '=?', country_id)]")

    def _create_approval_activity(self, group=False, not_user_id=False, title='Activity', message=''):
        activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
        if group:
            for user in group.users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    note=f'{message}',
                    user_id=user.id,
                    summary=_(f'{title}')
                )
        elif not_user_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                note=f'{message}',
                user_id=not_user_id.id,
                summary=_(f'{title}')
            )

    # Buttons
    def action_stage_draft(self):
        self.stage = "draft"

    def action_dep_manager_approve_tender(self):
        if not self.env.user.has_group("advicts_change_request_ticket.procurement_department_manager_approval"):
            raise ValidationError("You Don't Have Access to Approve Tender")
        self.stage = "confirm"

    def action_tender_cancel(self):
        self.stage = "cancel"

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('change.request') or _('New')

        res = super(ChangeRequestTicket, self).create(vals)
        return res


class CrClassification(models.Model):
    _name = 'cr.classification'
    _description = "CR Classification"

    name = fields.Char(string='Name', translate=True, required=True)
    desc = fields.Char(string='Description', translate=True)


class CrImpactLine(models.Model):
    _name = 'cr.impact.line'
    _description = "Impact Line"

    name = fields.Char(string="Name", required=True)
    change_id = fields.Many2one('change.request', string="Change Request")


class CrEvaluationLine(models.Model):
    _name = 'cr.evaluation.line'
    _description = "Evaluation Line"

    name = fields.Char(string="Name", required=True)
    desc = fields.Char(string="Description")
    change_id = fields.Many2one('change.request', string="Change Request")


class HelpdeskTicket(models.Model):
    _inherit = 'sh.helpdesk.ticket'
    change_id = fields.Many2one('change.request')
