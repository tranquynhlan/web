# -*- coding: utf-8 -*-
"""Handle dashboard notification related tests.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from datetime import datetime

from django.test import TestCase

from dashboard.models import Bounty
from dashboard.notifications import amount_usdt_open_work, build_github_notification
from pytz import UTC


class DashboardNotificationsTestCase(TestCase):
    """Define tests for dashboard notifications."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web/issues/11',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=True,
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        self.natural_value = round(self.bounty.get_natural_value(), 4)
        self.usdt_value = f"({round(self.bounty.value_in_usdt, 2)} USD)" if self.bounty.value_in_usdt else ""
        self.absolute_url = self.bounty.get_absolute_url()
        self.amount_open_work = amount_usdt_open_work()
        self.bounty_owner = f"(@{self.bounty.bounty_owner_github_username})"

    def test_build_github_notification_new_bounty(self):
        """Test the dashboard helper build_github_notification method with new_bounty."""
        message = build_github_notification(self.bounty, 'new_bounty')
        assert message.startswith(f'__This issue now has a funding of {self.natural_value} {self.bounty.token_name}')
        assert self.usdt_value in message
        assert f'[here]({self.absolute_url})' in message
        assert f'${self.amount_open_work}' in message

    def test_build_github_notification_killed_bounty(self):
        """Test the dashboard helper build_github_notification method with killed_bounty."""
        message = build_github_notification(self.bounty, 'killed_bounty')
        assert message.startswith(f"__The funding of {self.natural_value} {self.bounty.token_name} {self.usdt_value}")
        assert 'Questions?' in message
        assert f'${self.amount_open_work}' in message

    def tearDown(self):
        """Perform cleanup for the testcase."""
        self.bounty.delete()
