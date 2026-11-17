import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PitchPerfect",
  description: "Tailor your resume to any job description in minutes.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
