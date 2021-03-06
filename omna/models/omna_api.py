# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import requests
import base64
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone, time
from odoo import models, api, exceptions

_logger = logging.getLogger(__name__)


class OmnaApi(models.AbstractModel):
    """
       Model to connect to Omna's API
    """
    _name = "omna.api"
    _description = "Omna Api"

    @api.model
    def get(self, path, params={}):
        payload = self._sign_request(path, params)
        config = self.get_config()
        try:
            _logger.info("[GET] %s ? %s ", '%s/%s' % (config['omna_api_url'], path), payload)
            r = requests.get('%s/%s' % (config['omna_api_url'], path), payload)
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError("Error trying to connect to Omna's API.")
        if 200 <= r.status_code < 300:
            return r.json()

        try:
            error = r.json()
            _logger.error(error)
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError("Omna's API returned with errors")

        if 400 <= error.get('code', 400) < 500:
            raise exceptions.AccessError(error.get('message', "Error trying to connect to Omna's API."))

        raise exceptions.ValidationError(error.get('message', "Omna's API returned with errors"))

    @api.model
    def post(self, path, params={}):
        payload = self._sign_request(path, params)
        config = self.get_config()
        try:
            _logger.info("[POST] %s ? %s", '%s/%s' % (config['omna_api_url'], path), payload)
            r = requests.post('%s/%s' % (config['omna_api_url'], path), json=payload, headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError("Error trying to connect to Omna's API.")
        if 200 <= r.status_code < 300:
            return r.json()

        try:
            error = r.json()
            _logger.error(error)
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError("Omna's API returned with errors")

        if 400 <= error.get('code', 400) < 500:
            raise exceptions.AccessError(error.get('message', "Error trying to connect to Omna's API."))

        raise exceptions.ValidationError(error.get('message', "Omna's API returned with errors"))

    @api.model
    def patch(self, path, params={}):
        payload = self._sign_request(path, params)
        config = self.get_config()
        try:
            _logger.info("[PATCH] %s ? %s", '%s/%s' % (config['omna_api_url'], path), payload)
            r = requests.patch('%s/%s' % (config['omna_api_url'], path), json=payload, headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError("Error trying to connect to Omna's API.")
        if 200 <= r.status_code < 300:
            return r.json()

        try:
            error = r.json()
            _logger.error(error)
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError("Omna's API returned with errors")

        if 400 <= error.get('code', 400) < 500:
            raise exceptions.AccessError(error.get('message', "Error trying to connect to Omna's API."))

        raise exceptions.ValidationError(error.get('message', "Omna's API returned with errors"))

    @api.model
    def delete(self, path, params={}):
        payload = self._sign_request(path, params)
        config = self.get_config()
        try:
            _logger.info("[DEL] %s {%s}", '%s/%s' % (config['omna_api_url'], path), payload)
            r = requests.delete('%s/%s' % (config['omna_api_url'], path), json=payload, headers={'Content-Type': 'application/json'})
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError("Error trying to connect to Omna's API.")

        if 200 <= r.status_code < 300:
            return True

        try:
            error = r.json()
            _logger.error(error)
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError("Omna's API returned with errors")

        if 400 <= error.get('code', 400) < 500:
            raise exceptions.AccessError(error.get('message', "Error trying to connect to Omna's API."))

        raise exceptions.ValidationError(error.get('message', "Omna's API returned with errors"))

    @api.model
    def _sign_request(self, path, params={}):
        payload = params.copy()
        config = self.get_config()
        timestamp = datetime.now(timezone.utc)
        payload['token'] = config['cenit_user_token']
        payload['timestamp'] = int(datetime.timestamp(timestamp) * 1000)
        chars = (json.dumps(payload, separators=(',', ':')).replace('"', '')).replace("'", '')
        data_msg = [char for char in chars]
        data_msg.sort()
        msg = path + ''.join(data_msg)
        signature = hmac.new(bytes(config['cenit_user_secret'], 'utf-8'), msg=bytes(msg, 'utf-8'),
                             digestmod=hashlib.sha256).hexdigest()
        payload['hmac'] = signature
        return payload

    @api.model
    def get_config(self):
        icp = self.env['ir.config_parameter']
        tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        config = {
            'omna_api_url': icp.sudo().get_param(
                "omna_odoo.cenit_url", default='https://cenit.io/app/ecapi_v1'
            ),
            'cenit_user_secret': tenant.secret,
            'cenit_user_token': tenant.token,
        }

        return config
