const API_BASE_URL = "https://e1ncymtrq5.execute-api.us-east-1.amazonaws.com";

export async function runResearch(topic) {
  const response = await fetch(`${API_BASE_URL}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ topic }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}