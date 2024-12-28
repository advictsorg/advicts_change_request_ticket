/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class CrDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.orm = useService("orm");

        this.state = useState({
            crStats: {
                'total_cr': 0,
                'active_cr': 0,
                'cr_in_process': 0,
            },
        });

        useSubEnv({
            config: {
                ...getDefaultConfig(),
                ...this.env.config,
            },
        });


        this.crTimeline = useRef('crTimeline');

        onWillStart(async () => {
            let crData = await this.orm.call('cr.dashboard', 'get_cr_stats', []);
            if (crData) {
                this.state.crStats = crData;
            }
        });

        onMounted(() => {
            this.rendercrTimeline();
        })
    }
    viewcrStatic(type) {
        let name, context;
        let model = 'change.request';
        let domain = [];
        if (type == 'all') {
            name = 'Total CR'
            context = { 'create': false }
        } else if (type == 'active_cr') {
            name = 'Active CR'
            domain = [['stage', '=', 'done']]
            context = { 'create': false}
        } else if (type == 'in_progress') {
            name = 'In Progress'
            domain = [['stage', 'not in', ['draft', 'cancel','done']]]
            context = { 'create': false, 'search_default_group_by_stage': 1 }
        }
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: model,
            view_mode: 'list',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
            context: context,
            domain: domain,
        });

    }


    rendercrTimeline() {
        let data = this.state.crStats['cr_time_line']
        let cr_data = []
        for (const ss of data) {
            cr_data.push({
                'data': [{
                    'x': ss['name'],
                    'y': [new Date(ss['start_date']).getTime(), new Date(ss['end_date']).getTime()],
                    fillColor: '#87E8AE'
                }]
            })
        }
        const options = {
            series: cr_data,
            chart: {
                height: '375px',
                type: 'rangeBar'
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    distributed: true,
                    barHeight: '30%',
                    dataLabels: {
                        hideOverflowingLabels: false
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: function (val, opts) {
                    var label = opts.w.globals.labels[opts.dataPointIndex]
                    var a = moment(val[0])
                    var b = moment(val[1])
                    var diff = b.diff(a, 'days')
                    return '' + diff + (diff > 1 ? ' days' : ' day')
                },
                style: {
                    colors: ['#000000']
                }
            },
            xaxis: {
                type: 'datetime'
            },
            yaxis: {
                show: true,
                labels: {
                    show: true,
                    align: 'center',

                },
            },
            legend: {
                show: false,

            },

        };
        this.renderGraph(this.crTimeline.el, options);
    }
    renderGraph(el, options) {
        const graphData = new ApexCharts(el, options);
        graphData.render();
    }

}
CrDashboard.template = "advicts_change_request_ticket.template_cr_dashboard";
registry.category("actions").add("cr_dashboard", CrDashboard);