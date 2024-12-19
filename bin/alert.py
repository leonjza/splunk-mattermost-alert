import sys
import json
from dataclasses import dataclass, field
from typing import Optional

import requests

import log


@dataclass
class Config:
    """ Configuration for an incoming alert """

    webhook_url: str
    channel: Optional[str] = "splunk-alerts"
    severity: Optional[str] = "info"
    fields: Optional[str] = field(default=None)

    def validate(self):
        if not self.webhook_url:
            raise ValueError('webhook_url must be set')

        if self.severity not in ['none', 'info', 'warning', 'error']:
            raise ValueError('severity must be one of "none", "info", "warning", "error"')


class Alert:
    """ A Splunk alert. """

    payload: dict
    config: Config

    severity_map = {
        'none': '',
        'info': '✅',
        'warning': '⚠️',
        'error': '‼️'
    }

    def __init__(self):
        # grab the incoming alert
        data = sys.stdin.read()
        self.payload = json.loads(data)
        # log.debug('incoming payload', data)

        # parse configuration
        self.config = Config(**self.param('configuration', {}))
        log.debug('config', str(self.config))
        self.config.validate()

    def param(self, name, default=None):
        """
            Get a parameter from the alert.

            :param name:
            :param default:
            :return:
        """

        return self.payload.get(name, default)

    def severity(self) -> str:
        """
            Return the icon to display for the configured severity.

            :return:
        """

        return self.severity_map.get(self.config.severity)

    def fields_to_markdown(self) -> str:
        """
            Extract the relevant fields from the alert payload, returning
            a markdown-formatted table.

            Fields are comma-separated strings and can have wildcards. i.e., user.*

            :return: str - Markdown formatted table
        """

        if not self.config.fields:
            return ""

        results = self.param("result", {})
        extracted_fields = {}

        for candidate in self.config.fields.split(','):
            if candidate in results:
                extracted_fields[candidate] = results[candidate]
            elif "*" in candidate:
                prefix = candidate.rstrip("*")
                for key, value in results.items():
                    if key.startswith(prefix):
                        extracted_fields[key] = value

        if not extracted_fields:
            return ""

        # Convert extracted fields to a Markdown table
        markdown_table = "| Field        | Value        |\n"
        markdown_table += "|-------------|-------------|\n"
        for key, value in extracted_fields.items():
            markdown_table += f"| {key}       | {value}      |\n"

        return markdown_table

    def send(self):
        """
            Send the alert to Splunk

            :return:
        """

        alert_name = self.param('search_name', 'Unnamed Alert')
        alert_link = self.param('results_link')
        alert_fields = self.fields_to_markdown()

        message = {
            "channel": self.config.channel,
            "text": (
                f"{self.severity()} Alert: **{alert_name}**\n\n"
                "---\n"
                f"[View in Splunk]({alert_link})\n"
                # add markdown fields to the message if we had any
                f"\n\n"
                f"{alert_fields if alert_fields else ''}"
                "\n---"
            )
        }

        response = requests.post(self.config.webhook_url, json=message)
        response.raise_for_status()
