'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import Script from 'next/script';
import { usePathname, useRouter } from 'next/navigation';

export const TelegramContext = createContext<{
  telegram?: Telegram;
  isLoading: boolean;
}>({ isLoading: true });

export const TelegramProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [telegram, setTelegram] = useState<Telegram | undefined>(undefined);
  const [isLoading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Init Telegram Provider
  useEffect(() => {
    const app = window.Telegram;

    if (app) {
      app.WebApp.ready();
      app.WebApp.expand();
      app.WebApp.setHeaderColor('#000');
      app.WebApp.setBackgroundColor('#000');
      setTelegram(app);
      setLoading(false);
    }
  }, [pathname]);

  // BackButton logic
  useEffect(() => {
    if (telegram) {
      if (pathname !== '/') {
        telegram.WebApp.BackButton.show();
        telegram.WebApp.BackButton.onClick(() => router.back());
      } else {
        telegram.WebApp.BackButton.hide();
      }
    }
  }, [telegram, pathname, router]);

  // Init user
  useEffect(() => {
    if (telegram) {
      console.log(telegram);
      // createUser(telegram.WebApp.initData.user);
    }
  }, [telegram]);

  return (
    <TelegramContext.Provider value={{ telegram, isLoading }}>
      <Script
        src="https://telegram.org/js/telegram-web-app.js"
        strategy="beforeInteractive"
      />
      {children}
    </TelegramContext.Provider>
  );
};

export const useTelegram = () => useContext(TelegramContext);
