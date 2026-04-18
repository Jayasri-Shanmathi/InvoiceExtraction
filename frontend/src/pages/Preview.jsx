import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { saveInvoice } from "../services/invoiceApi";

// Confidence badge: green / yellow / red
function ConfidenceBadge({ score }) {
  if (score == null) return null;
  const pct = Math.round(score * 100);
  const color =
    pct >= 80 ? "bg-green-100 text-green-700" :
    pct >= 50 ? "bg-yellow-100 text-yellow-700" :
                "bg-red-100 text-red-700";
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
      {pct}% confidence
    </span>
  );
}

// Validation issues banner
function ValidationBanner({ validation }) {
  if (!validation) return null;
  const { status, issues } = validation;

  if (status === "valid") {
    return (
      <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
        ✅ Invoice passed validation
      </div>
    );
  }

  return (
    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm">
      <p className="font-semibold text-red-700 mb-1">⚠️ Validation issues found:</p>
      <ul className="list-disc list-inside text-red-600 space-y-0.5">
        {issues.map((issue, i) => <li key={i}>{issue}</li>)}
      </ul>
    </div>
  );
}

export default function Preview() {
  const location = useLocation();
  const navigate = useNavigate();

  const rawState = location.state || {};
  const [invoice, setInvoice] = useState(rawState.data || {});
  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState(null);

  const validation = rawState.validation;
  const confidence_score = rawState.confidence_score;

  // If landed here without data (e.g. direct URL), go back to upload
  if (!rawState.data) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500 mb-4">No invoice data found.</p>
        <button
          onClick={() => navigate("/upload")}
          className="px-4 py-2 bg-green-600 text-white rounded-lg"
        >
          Go to Upload
        </button>
      </div>
    );
  }

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
      setSaveResult({ type: "success", ...res });
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;
      if (detail?.error === "duplicate_invoice") {
        setSaveResult({
          type: "duplicate",
          message: detail.message,
          matched: detail.matched_invoice_number,
        });
      } else {
        alert("Failed to save invoice");
      }
    } finally {
      setSaving(false);
    }
  };

  const inputClass = "border border-gray-300 px-2 py-1 w-full rounded text-sm focus:outline-none focus:border-green-500";
  const labelClass = "text-xs text-gray-500 capitalize";

  return (
    <div className="p-6 min-h-screen bg-gray-100 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Preview & Edit Invoice</h1>
        <ConfidenceBadge score={confidence_score} />
      </div>

      {/* Validation banner */}
      <ValidationBanner validation={validation} />

      {/* Save result */}
      {saveResult?.type === "duplicate" && (
        <div className="mb-4 p-3 bg-orange-50 border border-orange-300 rounded-lg text-sm text-orange-700">
          🔁 {saveResult.message}
          {saveResult.matched && (
            <span className="ml-1 font-semibold">
              (matches invoice #{saveResult.matched})
            </span>
          )}
          <p className="mt-1 text-xs text-orange-500">This invoice was not saved.</p>
        </div>
      )}

      {saveResult?.type === "success" && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          ✅ {saveResult.message}
          {saveResult.analytics && (
            <div className="mt-2 space-y-1 text-xs text-blue-600">
              {saveResult.analytics.anomaly?.is_anomaly && (
                <p>⚠️ Anomaly detected: {saveResult.analytics.anomaly.reason}</p>
              )}
              {saveResult.analytics.vendor_analysis?.vendor_anomaly && (
                <p>⚠️ Vendor spike: {saveResult.analytics.vendor_analysis.reason}</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Vendor */}
      <Section title="Vendor">
        {["name", "address", "email", "gst_no", "contact"].map((key) => (
          <Field key={key} label={key} labelClass={labelClass}>
            <input
              className={inputClass}
              value={invoice.vendor?.[key] || ""}
              onChange={(e) => handleFieldChange("vendor", key, e.target.value)}
            />
          </Field>
        ))}
      </Section>

      {/* Invoice Header */}
      <Section title="Invoice Header">
        {["invoice_number", "invoice_date", "due_date", "invoice_amount", "ntby_no", "irn"].map((key) => (
          <Field key={key} label={key} labelClass={labelClass}>
            <input
              className={inputClass}
              value={invoice.invoice_header?.[key] || ""}
              onChange={(e) => handleFieldChange("invoice_header", key, e.target.value)}
            />
          </Field>
        ))}
      </Section>

      {/* Items */}
      <Section title="Line Items">
        {invoice.items?.map((item, idx) => (
          <div key={idx} className="mb-3 border border-gray-200 p-3 rounded-lg bg-white">
            <p className="text-xs font-semibold text-gray-400 mb-2">Item {idx + 1}</p>
            <div className="grid grid-cols-2 gap-2">
              {["code", "description", "uom", "billed_qty", "rate", "discount_percent",
                "taxable_value", "hsn_code", "cgst_percent", "cgst_amount",
                "sgst_percent", "sgst_amount", "igst_percent", "igst_amount", "total_value"].map((key) => (
                <Field key={key} label={key} labelClass={labelClass}>
                  <input
                    className={inputClass}
                    value={item[key] ?? ""}
                    onChange={(e) => handleFieldChange("items", key, e.target.value, idx)}
                  />
                </Field>
              ))}
            </div>
          </div>
        ))}
      </Section>

      {/* Summary */}
      <Section title="Summary">
        <div className="grid grid-cols-2 gap-2">
          {["taxable_value_total", "cgst_total", "sgst_total", "igst_total",
            "freight_charges", "tcs_percent", "tcs_amount", "roundoff_amount", "grand_total", "buyer_name"].map((key) => (
            <Field key={key} label={key} labelClass={labelClass}>
              <input
                className={inputClass}
                value={invoice.summary?.[key] ?? ""}
                onChange={(e) =>
                  setInvoice({ ...invoice, summary: { ...invoice.summary, [key]: e.target.value } })
                }
              />
            </Field>
          ))}
        </div>
      </Section>

      {/* Actions */}
      <div className="flex gap-3 mt-4">
        <button
          onClick={() => navigate("/upload")}
          className="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50"
        >
          ← Back
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-60"
        >
          {saving ? "Saving..." : "Save Invoice"}
        </button>
      </div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="mb-5 bg-white rounded-xl shadow-sm p-4">
      <h2 className="font-semibold text-gray-700 mb-3 border-b pb-1">{title}</h2>
      {children}
    </div>
  );
}

function Field({ label, labelClass, children }) {
  return (
    <div className="mb-2">
      <label className={labelClass}>{label.replace(/_/g, " ")}</label>
      {children}
    </div>
  );
}
