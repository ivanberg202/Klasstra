export function base64UrlDecode(base64Url) {
  console.log('Decoding base64Url:', base64Url);
  try {
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => `%${`00${c.charCodeAt(0).toString(16)}`.slice(-2)}`)
        .join('')
    );
    console.log('Decoded payload:', jsonPayload);
    return jsonPayload;
  } catch (error) {
    console.error('Error decoding base64Url:', error);
    throw error;
  }
}