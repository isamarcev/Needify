'use client';

import { TonConnectUIProvider } from '@tonconnect/ui-react';

export function TonConnectProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TonConnectUIProvider manifestUrl="https://tot-omega.vercel.app/tonconnect-manifest.json">
      {children}
    </TonConnectUIProvider>
  );
}
