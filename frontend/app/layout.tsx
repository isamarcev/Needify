import type { Metadata } from 'next';
import './globals.css';
import { TelegramProvider } from '@/providers/TelegramContext';
import {
  CssBaseline,
  Experimental_CssVarsProvider as CssVarsProvider,
} from '@mui/material';

import { AppRouterCacheProvider } from '@mui/material-nextjs/v13-appRouter';
import theme from '@/theme';
import { Inter } from 'next/font/google';
import { DateFnsProvider } from '@/providers/DateFnsProvider';
import { TonConnectProvider } from '@/providers/TonConnectProvider';

export const metadata: Metadata = {
  title: 'The Open Times',
  description:
    'A platform that helps people assist each other and exchange their TIME for more efficient economic growth, enabling them to live and work during their free time',
};

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          <DateFnsProvider>
            <CssVarsProvider theme={theme}>
              <TonConnectProvider>
                <TelegramProvider>{children}</TelegramProvider>
              </TonConnectProvider>
              <CssBaseline />
            </CssVarsProvider>
          </DateFnsProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
