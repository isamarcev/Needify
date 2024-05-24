import { toNano } from '@ton/core';
import { NativeWallet } from '../wrappers/NativeWallet';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const nativeWallet = provider.open(await NativeWallet.fromInit());

    await nativeWallet.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(nativeWallet.address);

    // run methods on `nativeWallet`
}
