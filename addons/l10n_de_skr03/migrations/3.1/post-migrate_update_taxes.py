# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra.addons.account.models.chart_template import update_taxes_from_templates


def migrate(cr, version):
    update_taxes_from_templates(cr, 'l10n_de_skr03.l10n_de_chart_template')
