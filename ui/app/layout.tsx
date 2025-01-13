import type { Metadata } from "next";
import "./globals.css";
import { WalletProvider } from "@/app/providers/WalletProvider";
import { MINTING_TOKEN_NAME } from "@/app/constants/appConfig";
import { Inter } from "next/font/google";
import { Bounce, ToastContainer } from "react-toastify";

export const metadata: Metadata = {
  title: MINTING_TOKEN_NAME,
  description: `An example minting UI for ${MINTING_TOKEN_NAME}`,
};

export const primaryFont = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${primaryFont.className} antialiased`}>
        <WalletProvider>
          <div className="flex min-h-screen">
            <div className="flex-grow items-center justify-center flex flex-col">
              <main>
                {children}
                <ToastContainer
                  position="bottom-right"
                  autoClose={5000}
                  hideProgressBar={false}
                  newestOnTop={false}
                  closeOnClick={false}
                  rtl={false}
                  pauseOnFocusLoss
                  draggable
                  pauseOnHover
                  theme="light"
                  transition={Bounce}
                />
              </main>
            </div>
          </div>
        </WalletProvider>
      </body>
    </html>
  );
}
