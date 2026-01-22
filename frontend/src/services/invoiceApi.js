import API from "./api";

export const uploadInvoice = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post("/Upload-file/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data.data; // extracted invoice JSON
};

export const saveInvoice = async (invoiceData) => {
  const res = await API.post("/save-invoice/", invoiceData);
  return res.data;
};
