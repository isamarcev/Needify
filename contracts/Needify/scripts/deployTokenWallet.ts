import { toNano } from '@ton/core';
import { TokenWallet } from '../wrappers/TokenWallet';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const tokenWallet = provider.open(await TokenWallet.fromInit());

    await tokenWallet.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(tokenWallet.address);

    // run methods on `tokenWallet`
}
