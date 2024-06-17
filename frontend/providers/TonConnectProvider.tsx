'use client';

import { TonConnectUIProvider } from '@tonconnect/ui-react';

export function TonConnectProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // https://tot-omega.vercel.app
    <TonConnectUIProvider manifestUrl="http://localhost:3000/tonconnect-manifest.json">
      {children}
    </TonConnectUIProvider>
  );
}
