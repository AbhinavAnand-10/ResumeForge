import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ResumeForge AI — Diagnostic-Grade Resume Optimization",
  description:
    "An honest ATS diagnosis, a guardrailed AI rewrite, and a real skill-gap plan. Nothing fabricated.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="grain-overlay" />
        {children}
      </body>
    </html>
  );
}
