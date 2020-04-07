# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime


class Payment(Document):
	def on_submit(self):
		if self.status != "Paid":
			frappe.throw("Cannot submit if payment failed")

		doc = frappe.get_doc(
			{
				"doctype": "Payment Ledger Entry",
				"amount": self.amount,
				"purpose": "Payment",
				"team": self.team,
				"reference_doctype": "Payment",
				"reference_name": self.name,
			}
		)
		doc.insert()
		doc.submit()


def process_stripe_webhook(doc, method):
	"""This method runs after a Stripe Webhook Log is created"""
	if doc.event_type not in ["invoice.payment_succeeded", "invoice.payment_failed"]:
		return

	event = frappe.parse_json(doc.payload)
	invoice = event["data"]["object"]
	customer_id = invoice["customer"]
	# value is in cents or paise
	amount = invoice["total"] / 100

	failed_payment = frappe.db.get_value(
		"Payment", {"status": "Failed", "stripe_invoice_id": invoice["id"]}
	)
	if failed_payment:
		payment = frappe.get_doc("Payment", failed_payment)
	else:
		team = frappe.db.get_value("Team", {"stripe_customer_id": customer_id}, "name")
		payment = frappe.get_doc(
			{
				"doctype": "Payment",
				"team": team,
				"amount": amount,
				"stripe_invoice_id": invoice["id"],
				"payment_link": invoice["hosted_invoice_url"],
			}
		)

	if doc.event_type == "invoice.payment_succeeded":
		payment.payment_date = datetime.fromtimestamp(
			invoice["status_transitions"]["paid_at"]
		)
		payment.status = "Paid"
		payment.save()
		payment.submit()
	elif doc.event_type == "invoice.payment_failed":
		payment.status = "Failed"
		payment.save()
