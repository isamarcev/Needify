import { toNano } from '@ton/core';
import { JobOffer } from '../wrappers/JobOffer';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const jobOffer = provider.open(await JobOffer.fromInit());

    await jobOffer.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(jobOffer.address);

    // run methods on `jobOffer`
}
