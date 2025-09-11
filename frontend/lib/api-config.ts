export const getApiUrl = (path: string) => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return `${process.env.NEXT_PUBLIC_API_URL}${path}`;
  }
  // Fallback to production backend URL
  return `https://master-1-hsnb.onrender.com${path}`;
};
