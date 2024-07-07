'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import Script from 'next/script';
import { usePathname, useRouter } from 'next/navigation';
import { createUser, getUser, addUserWallet } from '@/services/api';
import { useTonConnectUI } from '@tonconnect/ui-react';

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
  const [tonConnectUI] = useTonConnectUI();
  // const wallet = tonConnectUI.onStatusChange

  useEffect(() => {
    const app = window.Telegram;

    if (app) {
      app.WebApp.ready();
      app.WebApp.expand();
      app.WebApp.setHeaderColor('#000');
      app.WebApp.setBackgroundColor('#000');
      setWebApp(app);
      setLoading(false);
      console.log(webApp)
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
      (async () => {
        if (webApp?.WebApp.initDataUnsafe?.user) {
          const user = await getUser(webApp.WebApp.initDataUnsafe.user.id);
          // console.log(user.error)
          if (user.error) {
            await createUser({
              telegram_id: webApp.WebApp.initDataUnsafe.user.id,
              first_name: webApp.WebApp.initDataUnsafe.user.first_name,
              username: webApp.WebApp.initDataUnsafe.user.username,
              last_name: webApp.WebApp.initDataUnsafe.user.last_name,
            });
          }
        }
      })();
  }, [webApp]);

  // useEffect(() => {
  //   window.addEventListener('ton-connect-connection-completed', ((
  //     event: CustomEvent,
  //   ) => {
  //     if (event.detail.custom_data.chain_id !== "-3") {
  //       tonConnectUI.disconnect();
  //       webApp?.WebApp.showAlert('You are trying to connect with mainnet. Please connect with TESTNET.');
  //       return;
  //     }
  //     (async () => {
  //       if (!webApp?.WebApp?.initDataUnsafe?.user?.id) {
  //         return;
  //       }
  //       console.log('ton-connect-connection-completed', event);
  //       const user = await getUser(webApp.WebApp.initDataUnsafe.user.id);
  //       console.log('USER:');
  //       console.log(user);
  //       if (user.web3_wallet) {
  //         if (user.web3_wallet.address !== event.detail.wallet_address) {
  //           tonConnectUI.disconnect();
  //           webApp.WebApp.showAlert('You are trying to connect with another wallet');
  //         }
  //       }
  //       else {
  //         console.log(event.detail.wallet_address);
  //         await addUserWallet(webApp.WebApp.initDataUnsafe.user.id, {
  //           address: event.detail.wallet_address,
  //         });
  //       }
  //     })();
  //   }) as EventListener);
  //   window.addEventListener('ton-connect-disconnection', (event) => {
  //     console.log('ton-connect-disconnection', event);
  //   });
  // }, []);



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
