const API_BASE_URL = "https://e1ncymtrq5.execute-api.us-east-1.amazonaws.com";

export async function startResearch(topic) {
  const response = await fetch(`${API_BASE_URL}/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic }),
  });

  if (!response.ok) {
    throw new Error(`Failed to start research: ${response.status}`);
  }

  const data = await response.json();
  return data.execution_arn;
}

export async function checkStatus(executionArn) {
  const response = await fetch(
    `${API_BASE_URL}/status?execution_arn=${encodeURIComponent(executionArn)}`
  );

  if (!response.ok) {
    throw new Error(`Failed to check status: ${response.status}`);
  }

  return response.json();
}