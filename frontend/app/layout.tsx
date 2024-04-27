import type { Metadata } from 'next';
import './globals.css';
import { TelegramProvider } from '@/helpers/TelegramContext/TelegramContext';
import {
  CssBaseline,
  Experimental_CssVarsProvider as CssVarsProvider,
} from '@mui/material';

import { AppRouterCacheProvider } from '@mui/material-nextjs/v13-appRouter';
import theme from '@/theme';
import { Inter } from 'next/font/google';

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
        <CssBaseline />
        <AppRouterCacheProvider options={{ enableCssLayer: true }}>
          <CssVarsProvider theme={theme}>
            <TelegramProvider>{children}</TelegramProvider>
          </CssVarsProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
