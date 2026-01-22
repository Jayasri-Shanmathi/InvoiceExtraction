import { useLocation } from "react-router-dom";
import { useState } from "react";
import { saveInvoice } from "../services/invoiceApi";

export default function Preview() {
  const location = useLocation();
  const [invoice, setInvoice] = useState(location.state?.data || {});
  const [saving, setSaving] = useState(false);

  const handleFieldChange = (section, key, value, idx = null) => {
    if (section === "vendor" || section === "invoice_header") {
      setInvoice({ ...invoice, [section]: { ...invoice[section], [key]: value } });
    }

    if (section === "items") {
      const updatedItems = [...invoice.items];
      updatedItems[idx][key] = value;
      setInvoice({ ...invoice, items: updatedItems });
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const res = await saveInvoice(invoice);
      alert(res.message || "Invoice saved!");
    } catch (err) {
      console.error(err);
      alert("Failed to save invoice");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 min-h-screen bg-gray-100">
      <h1 className="text-2xl font-bold mb-4">Preview & Edit Invoice</h1>

      {/* Vendor */}
      <div className="mb-4">
        <h2 className="font-semibold">Vendor</h2>
        {["name", "address", "email", "gst_no", "contact"].map((key) => (
          <div key={key} className="mb-1">
            <label>{key}</label>
            <input
              className="border px-2 py-1 w-full"
              value={invoice.vendor?.[key] || ""}
              onChange={(e) => handleFieldChange("vendor", key, e.target.value)}
            />
          </div>
        ))}
      </div>

      {/* Invoice Header */}
      <div className="mb-4">
        <h2 className="font-semibold">Invoice Header</h2>
        {["invoice_number", "invoice_date", "due_date", "invoice_amount"].map(
          (key) => (
            <div key={key} className="mb-1">
              <label>{key}</label>
              <input
                className="border px-2 py-1 w-full"
                value={invoice.invoice_header?.[key] || ""}
                onChange={(e) =>
                  handleFieldChange("invoice_header", key, e.target.value)
                }
              />
            </div>
          )
        )}
      </div>

      {/* Items */}
      <div className="mb-4">
        <h2 className="font-semibold">Items</h2>
        {invoice.items?.map((item, idx) => (
          <div
            key={idx}
            className="mb-2 border p-2 rounded bg-white space-y-1"
          >
            {["code", "description", "billed_qty", "rate", "total_value"].map(
              (key) => (
                <div key={key}>
                  <label>{key}</label>
                  <input
                    className="border px-2 py-1 w-full"
                    value={item[key] || ""}
                    onChange={(e) =>
                      handleFieldChange("items", key, e.target.value, idx)
                    }
                  />
                </div>
              )
            )}
          </div>
        ))}
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="px-4 py-2 bg-green-600 text-white rounded"
      >
        {saving ? "Saving..." : "Save Invoice"}
      </button>
    </div>
  );
}
