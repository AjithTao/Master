export const getApiUrl = (path: string) => {
  // Check if we're in production (Vercel)
  if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    return `https://master-1-hsnb.onrender.com${path}`;
  }
  
  // Check for environment variable
  if (process.env.NEXT_PUBLIC_API_URL) {
    return `${process.env.NEXT_PUBLIC_API_URL}${path}`;
  }
  
  // Default to localhost for local development
  return `http://localhost:8000${path}`;
};
