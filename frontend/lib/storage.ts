export function getToken() {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null;
}
