# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

from configparser import ConfigParser
from os.path import join as opj
import os
import werkzeug.urls

import flectra
from flectra import models, fields


class IrTranslation(models.Model):

    _inherit = 'ir.translation'

    transifex_url = fields.Char("Transifex URL", compute='_get_transifex_url', help="Propose a modification in the official version of Flectra")

    def _get_transifex_url(self):
        """ Construct transifex URL based on the module on configuration """
        # e.g. 'https://www.transifex.com/flectra/'
        base_url = self.env['ir.config_parameter'].sudo().get_param('transifex.project_url')

        tx_config_file = ConfigParser()
        tx_sections = []
        for addon_path in flectra.addons.__path__:
            tx_path = opj(addon_path, '.tx', 'config')
            if os.path.isfile(tx_path):
                tx_config_file.read(tx_path)
                # first section is [main], after [flectra-11.sale]
                tx_sections.extend(tx_config_file.sections()[1:])

            # parent directory ad .tx/config is root directory in flectra/flectra
            tx_path = opj(addon_path, os.pardir, '.tx', 'config')
            if os.path.isfile(tx_path):
                tx_config_file.read(tx_path)
                tx_sections.extend(tx_config_file.sections()[1:])

        if not base_url or not tx_sections:
            self.update({'transifex_url': False})
        else:
            base_url = base_url.rstrip('/')

            # will probably be the same for all terms, avoid multiple searches
            translation_languages = list(set(self.mapped('lang')))
            languages = self.env['res.lang'].with_context(active_test=False).search(
                [('code', 'in', translation_languages)])

            language_codes = dict((l.code, l.iso_code) for l in languages)

            # .tx/config files contains the project reference
            # using ini files
            translation_modules = set(self.mapped('module'))
            project_modules = {}
            for module in translation_modules:
                for section in tx_sections:
                    if len(section.split(':')) != 6:
                        # old format ['main', 'flectra-16.base', ...]
                        tx_project, tx_mod = section.split(".")
                    else:
                        # tx_config_file.sections(): ['main', 'o:flectra:p:flectra-16:r:base', ...]
                        _, _, _, tx_project, _, tx_mod = section.split(':')
                    if tx_mod == module:
                        project_modules[module] = tx_project

            for translation in self:
                if not translation.module or not translation.src or translation.lang == 'en_US':
                    # custom or source term
                    translation.transifex_url = False
                    continue

                lang_code = language_codes.get(translation.lang)
                if not lang_code:
                    translation.transifex_url = False
                    continue

                project = project_modules.get(translation.module)
                if not project:
                    translation.transifex_url = False
                    continue

                # e.g. https://www.transifex.com/flectra/flectra-10/translate/#fr/sale/42?q=text:'Sale+Order'
                src = werkzeug.urls.url_quote_plus(translation.src[:50].replace("\n", "").replace("'", "\\'"))
                src = f"'{src}'" if "+" in src else src
                translation.transifex_url = "%(url)s/%(project)s/translate/#%(lang)s/%(module)s/42?q=%(src)s" % {
                    'url': base_url,
                    'project': project,
                    'lang': lang_code,
                    'module': translation.module,
                    'src': f"text%3A{src}",
                }
