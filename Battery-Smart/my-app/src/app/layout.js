import { Geist, Geist_Mono, Poppins } from "next/font/google";
import "./globals.css";

import Sidebar from "../components/sidebar/sidebar";
import Providers from "../components/Providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const poppins = Poppins({
  variable: "--font-poppins",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata = {
  title: "Battery Smart",
  description: "India's Largest Battery-Swapping Network for Electric Vehicles",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${poppins.variable} font-poppins antialiased`}
      >
        <Providers>
          <Sidebar>
            {children}
          </Sidebar>
        </Providers>
      </body>
    </html>
  );
}

