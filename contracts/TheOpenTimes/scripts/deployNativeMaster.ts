import { toNano } from '@ton/core';
import { NativeMaster } from '../wrappers/NativeMaster';
import { NetworkProvider } from '@ton/blueprint';

export async function run(provider: NetworkProvider) {
    const nativeMaster = provider.open(await NativeMaster.fromInit());

    await nativeMaster.send(
        provider.sender(),
        {
            value: toNano('0.05'),
        },
        {
            $$type: 'Deploy',
            queryId: 0n,
        }
    );

    await provider.waitForDeploy(nativeMaster.address);

    // run methods on `nativeMaster`
}
