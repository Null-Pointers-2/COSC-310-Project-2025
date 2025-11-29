import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css"; 
import { Navbar } from "@/../components/layout/Navbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Movie App",
  description: "Track and rate your favorite movies",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-gray-50`}>
        <Navbar />
        
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}