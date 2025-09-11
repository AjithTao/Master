export const getApiUrl = (path: string) => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://master-1-hsnb.onrender.com';
  // Ensure path starts with / and baseUrl doesn't end with /
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const cleanBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  return `${cleanBaseUrl}${cleanPath}`;
};
