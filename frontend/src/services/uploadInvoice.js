import API from "./api";

export const uploadInvoice = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await API.post("/Upload-file/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  console.log("RAW API RESPONSE:", res.data); // 👈 ADD THIS

  return res.data.data; // keep this
};
