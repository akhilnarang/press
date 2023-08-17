# Copyright (c) 2023, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Pod(Document):
	def before_insert(self):
		container = frappe.new_doc("Container")
		container.node = self.node
		container.stack = self.stack
		container.service = self.service
		container.ip_address = self.ip_address
		container.mac_address = self.mac_address
		container.insert()
		self.append("containers", {"container": container.name})
