import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 w-[400px] text-center">
        <h1 className="text-2xl font-bold mb-2">Invoice Intelligence</h1>
        <p className="text-gray-500 mb-8">
          Extract, validate, and analyze invoices using AI
        </p>

        <button
          onClick={() => navigate("/upload")}
          className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition mb-3"
        >
          Upload Invoice
        </button>

        <button
          onClick={() => navigate("/analytics")}
          className="w-full border border-gray-300 text-gray-600 py-2 rounded-lg hover:bg-gray-50 transition"
        >
          View Analytics
        </button>
      </div>
    </div>
  );
}
