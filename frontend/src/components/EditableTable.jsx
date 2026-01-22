export default function EditableTable({ data, setData }) {
  const handleChange = (section, key, value) => {
    setData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));
  };

  return (
    <div className="space-y-3">
      {Object.entries(data.invoice_header).map(([key, value]) => (
        <div key={key} className="grid grid-cols-3 items-center gap-4">
          <label className="text-sm font-medium capitalize">
            {key.replace(/_/g, " ")}
          </label>

          <input
            value={value || ""}
            onChange={(e) =>
              handleChange("invoice_header", key, e.target.value)
            }
            className="col-span-2 border border-gray-300 p-1 rounded"
          />
        </div>
      ))}
    </div>
  );
}
