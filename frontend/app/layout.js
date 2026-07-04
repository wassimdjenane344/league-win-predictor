import "./globals.css";

export const metadata = {
  title: "LoL Win Predictor",
  description: "Predict a League of Legends blue-side win probability from 10-minute match stats.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
