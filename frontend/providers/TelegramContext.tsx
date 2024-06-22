'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import Script from 'next/script';
import { usePathname, useRouter } from 'next/navigation';
import { createUser } from '@/services/api';

export const TelegramContext = createContext<{
  telegramApp?: Telegram;
  isLoading: boolean;
}>({ isLoading: true });

export const TelegramProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [webApp, setWebApp] = useState<Telegram | undefined>(undefined);
  const [isLoading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const app = window.Telegram;

    if (app) {
      app.WebApp.ready();
      app.WebApp.expand();
      app.WebApp.setHeaderColor('#000');
      app.WebApp.setBackgroundColor('#000');
      setWebApp(app);
      setLoading(false);
    }
  }, [pathname]);

  useEffect(() => {
    if (webApp) {
      if (pathname !== '/') {
        webApp.WebApp.BackButton.show();
        webApp.WebApp.BackButton.onClick(() => router.back());
      } else {
        webApp.WebApp.BackButton.hide();
      }
    }
  }, [webApp, pathname, router]);

  useEffect(() => {
    if (webApp && webApp.WebApp.initData.user) {
      createUser(webApp.WebApp.initData.user);
    }
  }, [webApp]);

  return (
    <TelegramContext.Provider value={{ telegramApp: webApp, isLoading }}>
      <Script
        src="https://telegram.org/js/telegram-web-app.js"
        strategy="beforeInteractive"
      />
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = () => useContext(TelegramContext);
