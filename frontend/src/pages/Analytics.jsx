import { useEffect, useState } from "react";
import { fetchAnalytics, fetchAlerts } from "../services/invoiceApi";
import { useNavigate } from "react-router-dom";

export default function Analytics() {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([fetchAnalytics(), fetchAlerts()])
      .then(([a, al]) => { setAnalytics(a); setAlerts(al); })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-gray-500">Loading analytics...</div>;
  if (error)   return <div className="p-8 text-red-500">Error: {error}</div>;

  return (
    <div className="p-6 min-h-screen bg-gray-100 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
        <button
          onClick={() => navigate("/upload")}
          className="text-sm border border-gray-300 px-3 py-1.5 rounded-lg hover:bg-gray-50"
        >
          ← Back
        </button>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label="Total Spend" value={`₹${analytics.total_spend?.toLocaleString()}`} color="green" />
        <KpiCard label="Anomalies" value={analytics.anomaly_count} color="orange" />
        <KpiCard label="Faulty Invoices" value={analytics.faulty_count} color="red" />
        <KpiCard label="Vendors" value={Object.keys(analytics.vendor_spend || {}).length} color="blue" />
      </div>

      {/* Vendor spend */}
      <Section title="Vendor-wise Spend">
        {Object.entries(analytics.vendor_spend || {}).length === 0
          ? <p className="text-gray-400 text-sm">No data yet</p>
          : Object.entries(analytics.vendor_spend).map(([vendor, amount]) => (
            <div key={vendor} className="flex justify-between items-center py-1.5 border-b last:border-0 text-sm">
              <span className="text-gray-700">{vendor}</span>
              <span className="font-semibold text-gray-800">₹{Number(amount).toLocaleString()}</span>
            </div>
          ))
        }
      </Section>

      {/* Monthly spend */}
      <Section title="Monthly Spend">
        {Object.entries(analytics.monthly_spend || {}).length === 0
          ? <p className="text-gray-400 text-sm">No data yet</p>
          : Object.entries(analytics.monthly_spend).map(([month, amount]) => (
            <div key={month} className="flex justify-between items-center py-1.5 border-b last:border-0 text-sm">
              <span className="text-gray-500">{month}</span>
              <span className="font-semibold">₹{Number(amount).toLocaleString()}</span>
            </div>
          ))
        }
      </Section>

      {/* Alerts */}
      <div className="grid md:grid-cols-3 gap-4">
        <AlertList title="⚠️ Faulty Invoices" items={alerts.faulty_invoices} color="red" />
        <AlertList title="📈 Anomalous Invoices" items={alerts.anomalous_invoices} color="orange" />
        <AlertList title="🔁 Duplicate Invoices" items={alerts.duplicate_invoices} color="yellow" />
      </div>
    </div>
  );
}

function KpiCard({ label, value, color }) {
  const colors = {
    green:  "bg-green-50 text-green-700 border-green-200",
    red:    "bg-red-50 text-red-700 border-red-200",
    orange: "bg-orange-50 text-orange-700 border-orange-200",
    blue:   "bg-blue-50 text-blue-700 border-blue-200",
  };
  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <p className="text-xs uppercase tracking-wide opacity-70">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-4 mb-4">
      <h2 className="font-semibold text-gray-700 mb-3 border-b pb-1">{title}</h2>
      {children}
    </div>
  );
}

function AlertList({ title, items, color }) {
  const colors = {
    red:    "bg-red-50 border-red-200",
    orange: "bg-orange-50 border-orange-200",
    yellow: "bg-yellow-50 border-yellow-200",
  };
  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <h3 className="font-semibold text-sm mb-2">{title}</h3>
      {!items?.length
        ? <p className="text-xs text-gray-400">None</p>
        : items.map((inv) => (
          <div key={inv.invoice_header_id} className="text-xs py-1 border-b last:border-0">
            <p className="font-medium">{inv.invoice_number || "—"}</p>
            <p className="text-gray-500">₹{inv.invoice_amount?.toLocaleString()} · score: {inv.confidence_score}</p>
            {inv.issues?.length > 0 && (
              <p className="text-red-500 mt-0.5">{inv.issues.join(", ")}</p>
            )}
          </div>
        ))
      }
    </div>
  );
}
