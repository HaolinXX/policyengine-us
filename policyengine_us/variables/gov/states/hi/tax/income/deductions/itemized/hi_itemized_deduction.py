from policyengine_us.model_api import *


class hi_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf"
    )
    defined_for = StateCode.HI
    def formula(tax_unit, period, parameters):
        # compute itemized deduction maximum
        p = parameters(period).gov.irs.deductions
        agi = tax_unit("adjusted_gross_income", period)
        itm_deds = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["Miscellaneous_deductions"]
        ]
        medical_and_dental_expenses = max(0, medical_and_dental_expenses - agi*p.Medical_and_dental_expenses)
        Miscellaneous_deductions = max(0, medical_and_dental_expenses - agi*p.Miscellaneous_deductions)
        itm_deds_max = medical_and_dental_expenses + Miscellaneous_deductions 
        # compute high-AGI limit on itemized deductions
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        # ... determine part of itemized deductions subject to limit
        excluded_itm_deds = add(tax_unit, period, p.limit.included_deductions)
        included_itm_deds = 0.8 * max_(
            0, itm_deds_max - excluded_itm_deds
        )
        # ... determine limit amount
        filing_status = tax_unit("filing_status", period)
        agi_limit = 0.03 * max_(
            0, agi - p.limit.agi_threshold[filing_status]
        )
        limit_amount = min_(included_itm_deds, agi_limit)
        # return limited itemized deductions
        return max_(0, itm_deds_max - limit_amount)
