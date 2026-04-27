import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

export const analyzeCode = async (code, language) => {
  try {
    const response = await axios.post(`${BASE_URL}/analyze`, {
      code,
      language,
    });
    return { data: response.data, error: null };
  } catch (err) {
    const message =
      err.response?.data?.error || err.message || "Something went wrong";
    return { data: null, error: message };
  }
};
