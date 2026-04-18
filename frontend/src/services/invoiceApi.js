import API from "./api";

export const uploadInvoice = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post("/Upload-file/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return {
    data: res.data.data,
    validation: res.data.validation,
    confidence_score: res.data.confidence_score,
  };
};

export const saveInvoice = async (invoiceData) => {
  const res = await API.post("/save-invoice/", invoiceData);
  return res.data;
};

export const fetchAnalytics = async () => {
  const res = await API.get("/analytics");
  return res.data;
};

export const fetchAlerts = async () => {
  const res = await API.get("/alerts");
  return res.data;
};
