export const metadata = {
  title: "Health Check V2",
  description: "CloudReady ERP Scorecard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
