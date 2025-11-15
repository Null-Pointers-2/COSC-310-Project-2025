// import { redirect } from "next/navigation";

export default async function ProtectedLayout({ children }: { children: React.ReactNode }) {
  // TODO: Add auth check
  return <>{children}</>;
}
