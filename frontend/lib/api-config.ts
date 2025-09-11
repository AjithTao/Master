export const getApiUrl = (path: string) => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return `${process.env.NEXT_PUBLIC_API_URL}${path}`;
  }
  return `http://localhost:8000${path}`;
};
