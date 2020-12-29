from __future__ import unicode_literals
import re
from past.builtins import cmp
import functools
import frappe, erpnext
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from erpnext.accounts.utils import get_fiscal_year
from frappe import _
from six import itervalues
from frappe.utils import (flt, getdate, get_first_day, add_months, add_days, formatdate, cstr, cint)
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_accounting_dimensions, get_dimension_with_children


def get_budget_data(
		company, root_type, period_list, filters=None,
		accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False,
		ignore_accumulated_values_for_fy=False , total = True):

	accounts = get_budget_accounts(company, root_type)
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_budget_accounts(accounts)

	company_currency = get_appropriate_currency(company, filters)

	budget_distribution_by_account = {}
	for root in frappe.db.sql("""select lft, rgt from tabAccount
			where root_type=%s and ifnull(parent_account, '') = ''""", root_type, as_dict=1):

		set_budget_distribution_by_account(
			company,
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft, root.rgt, filters,
			budget_distribution_by_account, ignore_closing_entries=ignore_closing_entries
		)
	calculate_values(
		accounts_by_name, budget_distribution_by_account, period_list, accumulated_values, ignore_accumulated_values_for_fy)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values)
	out = prepare_data(accounts, period_list, company_currency)
	out = filter_out_zero_value_rows(out, parent_children_map)

	if out and total:
		add_total_row(out, root_type, period_list, company_currency)

	return out

def get_appropriate_currency(company, filters=None):
	if filters and filters.get("presentation_currency"):
		return filters["presentation_currency"]
	else:
		return frappe.get_cached_value('Company',  company,  "default_currency")

def get_budget_accounts(company, root_type):
	return frappe.db.sql("""
		select name, account_number, parent_account, lft, rgt, root_type, report_type, account_name, include_in_gross, account_type, is_group, lft, rgt
		from `tabAccount`
		where company=%s and root_type=%s order by lft""", (company, root_type), as_dict=True)

def set_budget_distribution_by_account(
		company, from_date, to_date, root_lft, root_rgt, filters, budget_distribution_by_account, ignore_closing_entries=False):
	"""Returns a dict like { "account": [gl entries], ... }"""
	additional_conditions = get_additional_conditions(from_date, ignore_closing_entries, filters)

	accounts = frappe.db.sql_list("""select name from `tabAccount`
		where lft >= %s and rgt <= %s and company = %s""", (root_lft, root_rgt, company))

	if accounts:
		additional_conditions += " and ba.account in ({})"\
			.format(", ".join([frappe.db.escape(d) for d in accounts]))

		gl_filters = {
			"company": company,
			"from_date": from_date,
			"to_date": to_date,
			"finance_book": cstr(filters.get("finance_book"))
		}

		for key, value in filters.items():
			if value:
				gl_filters.update({
					key: value
				})

		budget_entries = frappe.db.sql("""
			select 
				fa.year_start_date, 
				b.budget_against, 
				b.cost_center, 
				b.project,
				b.payroll_entry, 
				b.fiscal_year, 
				ba.account, 
				ba.budget_amount, 
				b.monthly_distribution
			from 
				`tabBudget` b, 
				`tabBudget Account` ba, 
				`tabFiscal Year` fa 
			where
				b.name = ba.parent  
				and b.docstatus = 1				
				and b.fiscal_year = fa.name 
				and b.company=%(company)s {additional_conditions} 
				and fa.year_start_date >= %(from_date)s 
				and fa.year_end_date <= %(to_date)s 
			order by ba.account""".format(additional_conditions=additional_conditions), gl_filters, as_dict=True)


		for budget in budget_entries:
			if budget['monthly_distribution']:
				#print("dddd")
				get_distribution_budget_by_percentage(budget['account'], budget['fiscal_year'], budget['monthly_distribution'], budget['budget_amount'],budget_distribution_by_account)
			#else:
				#print("asdf")
				#get_distribution_budget(budget['account'], budget['fiscal_year'], budget['budget_amount'],budget_distribution_by_account)

		return budget_distribution_by_account

def get_distribution_budget_by_percentage(account, fiscal_year, monthly_distribution, budget_amount, budget_distribution_by_account):
	mdps = frappe.db.sql("""
		SELECT
			IF ( YEAR(fy.year_start_date ) = YEAR(fy.year_end_date),
					DATE(CONCAT_WS('-', md.fiscal_year, month(str_to_date(LEFT(mdp.month,3),'%%b')), 1))
        		, IF( MONTH(fy.year_start_date ) > month(str_to_date(LEFT(mdp.month,3),'%%b')),
              			DATE(CONCAT_WS('-', YEAR(fy.year_end_date ), month(str_to_date(LEFT(mdp.month,3),'%%b')), 1)),
              			DATE(CONCAT_WS('-', YEAR(fy.year_start_date), month(str_to_date(LEFT(mdp.month,3),'%%b')), 1))
            		)
        	) AS posting_date,
			md.fiscal_year,    		
			mdp.percentage_allocation,
			'' AS account,
			'' AS total_budget_amount
		FROM 
			`tabMonthly Distribution` md,
			`tabMonthly Distribution Percentage` mdp,
    		`tabFiscal Year` fy
		WHERE
			md.name = mdp.parent
    		and md.fiscal_year = fy.name
    		and md.fiscal_year = %(fiscal_year)s
    		and md.name = %(monthly_distribution)s """,{ "fiscal_year": fiscal_year, "monthly_distribution": monthly_distribution},as_dict=True)
	
	for v in mdps:
		v['account'] = account
		v['total_budget_amount'] = (budget_amount*v['percentage_allocation'])/100
		budget_distribution_by_account.setdefault(account, []).append(v)
	#print(budget_distribution_by_account)
	return budget_distribution_by_account
	
def get_distribution_budget(account, fiscal_year, budget_amount, budget_distribution_by_account):
	fiscal_year_start_date = frappe.db.get_value("Fiscal Year", fiscal_year, "year_start_date")
	v={
		"posting_date": '',
		"account": account,
		"fiscal_year": fiscal_year,
		"total_budget_amount":''
	}

	for x in range(12):		
		v["posting_date"] = add_months(fiscal_year_start_date, x)
		v["account"] = account
		v["total_budget_amount"] = (8.333 * budget_amount) / 100 
		budget_distribution_by_account.setdefault(account, []).append(v)
	#print(budget_distribution_by_account)
	return budget_distribution_by_account
	
def calculate_values(
		accounts_by_name, gl_entries_by_account, period_list, accumulated_values, ignore_accumulated_values_for_fy):
	for entries in itervalues(gl_entries_by_account):
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			if not d:
				frappe.msgprint(
					_("Could not retrieve information for {0}.".format(entry.account)), title="Error",
					raise_exception=1
				)
			for period in period_list:
				# check if posting date is within the period

				if entry.posting_date <= period.to_date:
					if (accumulated_values or entry.posting_date >= period.from_date) and \
						(not ignore_accumulated_values_for_fy or
							entry.fiscal_year == period.to_date_fiscal_year):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.total_budget_amount)

			#if entry.posting_date < period_list[0].year_start_date:
			#	d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)

def filter_budget_accounts(accounts, depth=20):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			sort_accounts(children, is_root=True if parent==None else False)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map

def sort_accounts(accounts, is_root=False, key="name"):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_accounts(a, b):
		if re.split('\W+', a[key])[0].isdigit():
			# if chart of accounts is numbered, then sort by number
			return cmp(a[key], b[key])
		elif is_root:
			if a.report_type != b.report_type and a.report_type == "Balance Sheet":
				return -1
			if a.root_type != b.root_type and a.root_type == "Asset":
				return -1
			if a.root_type == "Liability" and b.root_type == "Equity":
				return -1
			if a.root_type == "Income" and b.root_type == "Expense":
				return -1
		else:
			# sort by key (number) or name
			return cmp(a[key], b[key])
		return 1

	accounts.sort(key = functools.cmp_to_key(compare_accounts))

def get_additional_conditions(from_date, ignore_closing_entries, filters):
	additional_conditions = []

	accounting_dimensions = get_accounting_dimensions(as_list=False)

	if filters:
		if filters.get("project"):
			if not isinstance(filters.get("project"), list):
				filters.project = frappe.parse_json(filters.get("project"))

			additional_conditions.append("b.project in %(project)s")

		if filters.get("cost_center"):
			filters.cost_center = get_cost_centers_with_children(filters.cost_center)
			additional_conditions.append("b.cost_center in %(cost_center)s")

	if accounting_dimensions:
		for dimension in accounting_dimensions:
			if filters.get(dimension.fieldname):
				if frappe.get_cached_value('DocType', dimension.document_type, 'is_tree'):
					filters[dimension.fieldname] = get_dimension_with_children(dimension.document_type,
						filters.get(dimension.fieldname))
					additional_conditions.append("{0} in %({0})s".format(dimension.fieldname))
				else:
					additional_conditions.append("{0} in (%({0})s)".format(dimension.fieldname))

	return " and {}".format(" and ".join(additional_conditions)) if additional_conditions else ""

def accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = \
					accounts_by_name[d.parent_account].get(period.key, 0.0) + d.get(period.key, 0.0)

def prepare_data(accounts, period_list, company_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")

	for d in accounts:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict({
			"account": _(d.name),
			"parent_account": _(d.parent_account) if d.parent_account else '',
			"indent": flt(d.indent),
			"year_start_date": year_start_date,
			"year_end_date": year_end_date,
			"currency": company_currency,
			"include_in_gross": d.include_in_gross,
			"account_type": d.account_type,
			"is_group": d.is_group,			
			"account_name": ('%s - %s' %(_(d.account_number), _(d.account_name))
				if d.account_number else _(d.account_name))
		})
		for period in period_list:
			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if abs(row[period.key]) >= 0.005:
				# ignore zero values
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)

	return data

def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value"):
			data_with_value.append(d)
		else:
			# show group with zero balance, if there are balances against child
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						break

	return data_with_value

def add_total_row(out, root_type, period_list, company_currency):
	total_row = {
		"account_name": _("Total {0})").format(_(root_type)),
		"account": _("Total {0} )").format(_(root_type)),
		"currency": company_currency
	}

	for row in out:
		if not row.get("parent_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
				row[period.key] = row.get(period.key, 0.0)

			total_row.setdefault("total", 0.0)
			total_row["total"] += flt(row["total"])
			row["total"] = ""

	if "total" in total_row:
		out.append(total_row)

		# blank row after Total
		out.append({})

def get_cost_centers_with_children(cost_centers):
	if not isinstance(cost_centers, list):
		cost_centers = [d.strip() for d in cost_centers.strip().split(',') if d]

	all_cost_centers = []
	for d in cost_centers:
		if frappe.db.exists("Cost Center", d):
			lft, rgt = frappe.db.get_value("Cost Center", d, ["lft", "rgt"])
			children = frappe.get_all("Cost Center", filters={"lft": [">=", lft], "rgt": ["<=", rgt]})
			all_cost_centers += [c.name for c in children]
		else:
			frappe.throw(_("Cost Center: {0} does not exist".format(d)))

	return list(set(all_cost_centers))
