export const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname || 'localhost';
    return `http://${host}:8000`;
  }
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
};
