from typing import List, Dict, Any
from collections import Counter
from .models import Invoice

class ValidationResult:
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        self.is_valid = True
        self.errors: List[str] = []

    def add_error(self, message: str):
        self.is_valid = False
        self.errors.append(message)

    def to_dict(self):
        return {
            "invoice_id": self.invoice_id,
            "is_valid": self.is_valid,
            "errors": self.errors
        }

def validate_business_rules(invoice: Invoice) -> ValidationResult:
    result = ValidationResult(invoice.invoice_number)

    # Rule 1: Math Consistency
    calc_gross = invoice.totals.net_amount + invoice.totals.tax_amount
    if abs(calc_gross - invoice.totals.gross_amount) > 0.05:
        result.add_error(f"Math error: Net + Tax != Gross")

    # Rule 2: Line Item Consistency
    if invoice.line_items:
        line_sum = sum(item.line_total for item in invoice.line_items)
        if abs(line_sum - invoice.totals.net_amount) > 0.05:
            result.add_error(f"Line item mismatch: Sum != Net Total")

    # Rule 3: Date Logic
    if invoice.due_date and invoice.due_date < invoice.invoice_date:
        result.add_error("Date error: Due date before Invoice date")

    return result

def run_batch_validation(invoices_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = []
    valid_count = 0
    invalid_count = 0
    error_counts = Counter()
    seen_ids = set()
    
    for data in invoices_data:
        inv_id = data.get("invoice_number", "UNKNOWN")
        
        # Rule 4: Duplicates
        if inv_id in seen_ids:
            res = ValidationResult(inv_id)
            res.add_error("Duplicate Invoice detected")
            results.append(res.to_dict())
            invalid_count += 1
            error_counts["Duplicate Invoice"] += 1
            continue
        
        if inv_id != "UNKNOWN":
            seen_ids.add(inv_id)

        try:
            invoice_model = Invoice(**data)
        except Exception as e:
            res = ValidationResult(inv_id)
            res.add_error(f"Schema Error: {str(e)}")
            results.append(res.to_dict())
            invalid_count += 1
            error_counts["Schema Error"] += 1
            continue

        logic_result = validate_business_rules(invoice_model)
        
        if logic_result.is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            for err in logic_result.errors:
                key = err.split(":")[0] 
                error_counts[key] += 1
        
        results.append(logic_result.to_dict())

    return {
        "summary": {
            "total_processed": len(invoices_data),
            "valid_invoices": valid_count,
            "invalid_invoices": invalid_count,
            "error_distribution": dict(error_counts)
        },
        "details": results
    }
