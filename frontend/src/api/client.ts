import { API_BASE_URL } from "../../lib/config";

type FetchOptions<T = unknown> = Omit<RequestInit, "body"> & {
  body?: T;
};


export async function api(endpoint: string, options: FetchOptions = {}) {
  // TODO: Implement fetch logic here
  console.log(`API call to ${API_BASE_URL}${endpoint}`, options);
  return null; // stub returns null for now
}
