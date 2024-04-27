'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import Script from 'next/script';

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

  useEffect(() => {
    const app = window.Telegram;

    if (app) {
      app.WebApp.ready();
      app.WebApp.expand();
      setWebApp(app);
      setLoading(false);
    }
  }, []);

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
