import { toNano } from '@ton/core';
import { SimpleJetton } from '../wrappers/SimpleJetton';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const simpleJetton = provider.open(await SimpleJetton.fromInit());

    await simpleJetton.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(simpleJetton.address);

    // run methods on `simpleJetton`
}
