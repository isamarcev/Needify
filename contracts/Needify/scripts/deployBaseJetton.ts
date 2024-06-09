import { toNano } from '@ton/core';
import { BaseJetton } from '../wrappers/BaseJetton';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const baseJetton = provider.open(await BaseJetton.fromInit());

    await baseJetton.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(baseJetton.address);

    // run methods on `baseJetton`
}
