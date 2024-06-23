'use client';
import { TonConnectUIProvider } from '@tonconnect/ui-react';

const MANIFEST_URL = process.env.NEXT_PUBLIC_MANIFEST_URL;

export function TonConnectProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TonConnectUIProvider
      manifestUrl={`${MANIFEST_URL}/tonconnect-manifest.json`}
    >
      {children}
    </TonConnectUIProvider>
  );
}
