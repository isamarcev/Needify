'use client';
import { TonConnectUIProvider } from '@tonconnect/ui-react';

const MANIFEST_URL = process.env.MANIFEST_URL;

export function TonConnectProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TonConnectUIProvider
      manifestUrl={`https://raw.githubusercontent.com/isamarcev/CryptoWallet/TEMPORARY/web3_wallet_logo.json`}
    >
      {children}
    </TonConnectUIProvider>
  );
}
