import { useState } from "react";
import { uploadInvoice } from "../services/invoiceApi";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return alert("Please select an invoice");

    try {
      setLoading(true);
      const invoice = await uploadInvoice(file);

      navigate("/preview", { state: { data: invoice } });
    } catch (err) {
      console.error(err);
      alert("Invoice extraction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 w-[400px]">
        <h1 className="text-2xl font-bold text-center mb-2">
          Invoice Extraction
        </h1>
        <p className="text-gray-500 text-center mb-6">
          Upload an invoice to extract structured data
        </p>

        <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 cursor-pointer hover:border-green-500 transition">
          <span className="text-gray-500">
            {file ? file.name : "Click to upload invoice (PDF / Image)"}
          </span>
          <input
            type="file"
            accept="application/pdf,image/*"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </label>

        <button
          onClick={handleUpload}
          disabled={loading}
          className="w-full mt-6 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
        >
          {loading ? "Extracting..." : "Extract Invoice"}
        </button>

        {loading && (
          <p className="text-center text-gray-500 mt-3 animate-pulse">
            AI is reading your invoice...
          </p>
        )}
      </div>
    </div>
  );
}
